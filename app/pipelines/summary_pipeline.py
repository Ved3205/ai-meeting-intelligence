"""
app/pipelines/summary_pipeline.py

Orchestrates meeting-level intelligence generation for an ALREADY
INDEXED meeting:

    meeting_id -> MeetingContext (existing chunks)
               -> Summary / Title / Keywords / Action Items
                  (each via PromptFactory + LLMService)
               -> SummaryPipelineResult

This pipeline does NOT re-run video processing. It assumes the video
has already been transcribed, chunked, embedded, and uploaded via
`video_pipeline.py`.

See the module docstrings of `app.services.meeting_context_service` and
the "_call_llm" method below for two genuine architecture gaps this
pipeline had to work around using only documented public APIs -- both
are called out loudly rather than papered over.
"""

from __future__ import annotations

import logging
import re
import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.models.llm_request import LLMRequest
from app.models.prompt_request import PromptRequest

from app.prompts.registry.prompt_factory import PromptFactory

from app.services.llm_service import LLMService
from app.services.meeting_context_service import MeetingContext, MeetingContextService
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

MAX_KEYWORDS = 20

_NO_ACTION_ITEMS_PATTERNS = (
    "no action item",
    "none identified",
    "no explicit action item",
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class SummaryPipelineError(Exception):
    """Base exception for SummaryPipeline-level orchestration failures."""


class MeetingNotFoundError(SummaryPipelineError):
    """Raised when no indexed content exists for the given meeting_id."""


class EmptyMeetingContentError(SummaryPipelineError):
    """Raised when the meeting exists but has no usable transcript text."""


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------
@dataclass
class SummaryPipelineResult:
    """
    Meeting-level intelligence produced by SummaryPipeline.

    No equivalent result model exists in MODELS.md, so this is the
    smallest appropriate model for the four required outputs plus
    minimal run metadata.
    """

    meeting_id: str
    title: str
    summary: str
    keywords: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Optional[str]]] = field(default_factory=list)
    chunk_count: int = 0
    elapsed_time: float = 0.0


# ---------------------------------------------------------------------------
# Summary pipeline
# ---------------------------------------------------------------------------
class SummaryPipeline:
    """
    Orchestrates generation of Summary / Title / Keywords / Action
    Items for an already-indexed meeting.

    Contains no business logic: meeting context reconstruction, prompt
    construction, and LLM generation are all delegated to existing
    services and the existing prompt system through their public APIs.
    """

    def __init__(
        self,
        meeting_context_service: Optional[MeetingContextService] = None,
        llm_service: Optional[LLMService] = None,
        retrieval_service: Optional[RetrievalService] = None,
    ) -> None:
        """
        Args:
            meeting_context_service: Injected MeetingContextService.
                Defaults to a real instance (which itself defaults to a
                real `RetrievalService`, unless `retrieval_service` is
                also supplied here).
            llm_service: Injected LLMService instance. Defaults to a
                real `LLMService()`.
            retrieval_service: Injected RetrievalService, forwarded to
                the default `MeetingContextService` if
                `meeting_context_service` is not supplied. Ignored if
                `meeting_context_service` is supplied directly.
        """
        self.llm_service = llm_service or LLMService()
        self.meeting_context_service = meeting_context_service or MeetingContextService(
            retrieval_service=retrieval_service
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, meeting_id: str) -> SummaryPipelineResult:
        """
        Generate meeting-level intelligence for an already-indexed meeting.

        Args:
            meeting_id: Identifier of a meeting previously processed by
                `video_pipeline.py`.

        Returns:
            A `SummaryPipelineResult` with summary, title, keywords, and
            action items.

        Raises:
            ValueError: If `meeting_id` is empty/whitespace.
            MeetingNotFoundError: If no indexed chunks exist for this
                meeting_id.
            EmptyMeetingContentError: If chunks exist but contain no
                usable text.
            Exception: Any exception from the underlying services
                propagates unchanged after being logged with context.
                This pipeline never fabricates a result on failure.
        """
        start_time = time.perf_counter()
        logger.info("Starting summary pipeline")

        self._validate_meeting_id(meeting_id)
        meeting_id = meeting_id.strip()

        context = self._load_meeting_context(meeting_id)
        logger.info(
            "Loaded meeting context (meeting_id=%s, chunks=%d)",
            meeting_id,
            context.chunk_count,
        )

        summary = self._generate_summary(context)
        title = self._generate_title(context)
        keywords = self._generate_keywords(context)
        action_items = self._generate_action_items(context)

        elapsed = time.perf_counter() - start_time
        logger.info("Summary pipeline completed (meeting_id=%s, elapsed=%.2fs)", meeting_id, elapsed)

        return SummaryPipelineResult(
            meeting_id=meeting_id,
            title=title,
            summary=summary,
            keywords=keywords,
            action_items=action_items,
            chunk_count=context.chunk_count,
            elapsed_time=elapsed,
        )

    # ------------------------------------------------------------------
    # Context loading
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_meeting_id(meeting_id: str) -> None:
        if meeting_id is None or not isinstance(meeting_id, str) or not meeting_id.strip():
            raise ValueError("meeting_id must be a non-empty, non-whitespace string")

    def _load_meeting_context(self, meeting_id: str) -> MeetingContext:
        logger.info("Loading meeting context")
        context = self.meeting_context_service.get_context(meeting_id)

        if context.chunk_count == 0:
            raise MeetingNotFoundError(
                f"No indexed content found for meeting_id={meeting_id!r}. "
                f"Has this meeting been processed by video_pipeline.py?"
            )
        if not context.transcript_text.strip():
            raise EmptyMeetingContentError(
                f"Meeting {meeting_id!r} has indexed chunks but no usable text content."
            )
        return context

    # ------------------------------------------------------------------
    # Generation stages
    # ------------------------------------------------------------------
    def _generate_summary(self, context: MeetingContext) -> str:
        logger.info("Generating meeting summary")
        prompt = self._build_prompt("summary", context)
        return self._call_llm(prompt, stage="summary", meeting_id=context.meeting_id)

    def _generate_title(self, context: MeetingContext) -> str:
        logger.info("Generating title")
        prompt = self._build_prompt("title", context)
        return self._call_llm(prompt, stage="title", meeting_id=context.meeting_id)

    def _generate_keywords(self, context: MeetingContext) -> List[str]:
        logger.info("Extracting keywords")
        prompt = self._build_prompt("keywords", context)
        raw = self._call_llm(prompt, stage="keywords", meeting_id=context.meeting_id)
        return self._parse_keywords(raw)

    def _generate_action_items(self, context: MeetingContext) -> List[Dict[str, Optional[str]]]:
        logger.info("Generating action items")
        prompt = self._build_prompt("action_items", context)
        raw = self._call_llm(prompt, stage="action_items", meeting_id=context.meeting_id)
        return self._parse_action_items(raw)

    # ------------------------------------------------------------------
    # Prompt construction (existing PromptFactory system ONLY)
    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(prompt_type: str, context: MeetingContext) -> str:
        """
        Build a prompt using the existing PromptFactory system.

        Prompt builders may return either:
        - a fully rendered string, or
        - a PromptRequest containing the rendered question plus
            transcript/context fields.

        The LLMService receives a string in LLMRequest.question, so when a
        PromptRequest is returned we preserve its prompt question and append
        the transcript/context required by the pipeline contract.
        """
        request = PromptRequest(
            question=None,
            retrieved_chunks=[],
            transcript=context.transcript_text,
            metadata=None,
        )

        builder = PromptFactory.get_builder(prompt_type)
        built_prompt = builder.build(request)

        if isinstance(built_prompt, str):
            prompt_text = built_prompt
        elif isinstance(built_prompt, PromptRequest):
            prompt_text = built_prompt.question or ""

            # The current mock/test PromptFactory puts the prompt marker in
            # `question` while retaining the actual transcript separately.
            if built_prompt.transcript:
                prompt_text = f"{prompt_text}\n\n{built_prompt.transcript}"
        else:
            raise TypeError(
                f"{prompt_type} prompt builder returned unexpected type: "
                f"{type(built_prompt).__name__}"
            )

        return prompt_text

    # ------------------------------------------------------------------
    # LLM invocation
    # ------------------------------------------------------------------
    def _call_llm(
        self,
        prompt_text: str,
        *,
        stage: str,
        meeting_id: str,
    ) -> str:
        """
        Send an already-rendered specialized prompt directly to the LLM.

        SummaryPipeline uses PromptFactory to construct specialized
        summary/title/keyword/action-item prompts.

        These prompts must not be routed through generate_answer(),
        because generate_answer() is the QA API and requires retrieved
        chunks.
        """
        try:
            answer = self.llm_service.generate_from_prompt(prompt_text)
        except Exception:
            logger.exception(
                "%s generation failed (meeting_id=%s)",
                stage,
                meeting_id,
            )
            raise

        return answer.strip()

    # ------------------------------------------------------------------
    # Output parsing (heuristic -- no ActionItem/Keyword model exists)
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_keywords(raw: str) -> List[str]:
        """
        Parse a keyword-listing LLM response into a flat, ordered,
        deduplicated list of strings, capped at MAX_KEYWORDS.

        ASSUMPTION (no keyword model/schema is documented): the LLM
        response is either newline-separated or comma-separated,
        optionally with leading list markers ("-", "*", "1.").
        """
        if not raw or not raw.strip():
            return []

        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if len(lines) <= 1:
            lines = [item.strip() for item in raw.split(",") if item.strip()]

        keywords: List[str] = []
        seen = set()
        marker_pattern = re.compile(r"^[\-\*\u2022]|^\d+[\.\)]\s*")
        for line in lines:
            cleaned = marker_pattern.sub("", line).strip(" .")
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            keywords.append(cleaned)
            if len(keywords) >= MAX_KEYWORDS:
                break
        return keywords

    @staticmethod
    def _parse_action_items(raw: str) -> List[Dict[str, Optional[str]]]:
        """
        Parse an action-items LLM response into a list of
        {"description", "owner", "deadline"} dicts.

        Supports:
        - JSON arrays of action-item objects
        - labeled text blocks using Task/Description/Owner/Deadline
        - explicit no-action-item responses
        """
        if not raw or not raw.strip():
            return []

        raw = raw.strip()

        # --------------------------------------------------------------
        # First: JSON response
        # --------------------------------------------------------------
        try:
            parsed = json.loads(raw)

            if isinstance(parsed, list):
                items: List[Dict[str, Optional[str]]] = []

                for item in parsed:
                    if not isinstance(item, dict):
                        continue

                    description = item.get("description")
                    owner = item.get("owner")
                    deadline = item.get("deadline")

                    if description is None:
                        continue

                    description = str(description).strip()

                    if not description:
                        continue

                    owner = (
                        str(owner).strip()
                        if owner is not None and str(owner).strip()
                        else None
                    )

                    deadline = (
                        str(deadline).strip()
                        if deadline is not None and str(deadline).strip()
                        else None
                    )

                    if owner and owner.lower() in ("none", "n/a", "-"):
                        owner = None

                    if deadline and deadline.lower() in ("none", "n/a", "-"):
                        deadline = None

                    items.append(
                        {
                            "description": description,
                            "owner": owner,
                            "deadline": deadline,
                        }
                    )

                return items

        except (json.JSONDecodeError, TypeError):
            # Not JSON; continue with the labeled-text parser below.
            pass

        # --------------------------------------------------------------
        # Second: explicit no-action-items response
        # --------------------------------------------------------------
        task_pattern = re.compile(
            r"^(?:\d+[\.\)]\s*)?(?:Task|Description)\s*:\s*(.+)$",
            re.IGNORECASE,
        )
        owner_pattern = re.compile(
            r"^Owner\s*:\s*(.+)$",
            re.IGNORECASE,
        )
        deadline_pattern = re.compile(
            r"^Deadline\s*:\s*(.+)$",
            re.IGNORECASE,
        )

        has_structured_items = bool(
            re.search(r"(?:Task|Description)\s*:", raw, re.IGNORECASE)
        )

        lowered = raw.lower()

        if not has_structured_items and any(
            pattern in lowered for pattern in _NO_ACTION_ITEMS_PATTERNS
        ):
            return []

        # --------------------------------------------------------------
        # Third: labeled-text fallback
        # --------------------------------------------------------------
        blocks = re.split(
            r"\n\s*\n|\n(?=\d+[\.\)]\s)",
            raw,
        )

        items: List[Dict[str, Optional[str]]] = []

        for block in blocks:
            block = block.strip()

            if not block:
                continue

            description: Optional[str] = None
            owner: Optional[str] = None
            deadline: Optional[str] = None

            for line in block.splitlines():
                line = line.strip()

                if not line:
                    continue

                if match := task_pattern.match(line):
                    description = match.group(1).strip()

                elif match := owner_pattern.match(line):
                    value = match.group(1).strip()
                    owner = (
                        None
                        if value.lower() in ("none", "n/a", "-", "")
                        else value
                    )

                elif match := deadline_pattern.match(line):
                    value = match.group(1).strip()
                    deadline = (
                        None
                        if value.lower() in ("none", "n/a", "-", "")
                        else value
                    )

            if description is None:
                for line in block.splitlines():
                    line = line.strip()

                    if (
                        line
                        and not owner_pattern.match(line)
                        and not deadline_pattern.match(line)
                    ):
                        description = re.sub(
                            r"^\d+[\.\)]\s*",
                            "",
                            line,
                        ).strip()
                        break

            if description:
                items.append(
                    {
                        "description": description,
                        "owner": owner,
                        "deadline": deadline,
                    }
                )

        return items


# ---------------------------------------------------------------------------
# Convenience module-level function
# ---------------------------------------------------------------------------
def run_summary_pipeline(meeting_id: str) -> SummaryPipelineResult:
    """
    Convenience wrapper that constructs a `SummaryPipeline` with default,
    real service implementations and runs it once.

    Args:
        meeting_id: Identifier of an already-indexed meeting.

    Returns:
        The resulting `SummaryPipelineResult`.
    """
    pipeline = SummaryPipeline()
    return pipeline.run(meeting_id)
