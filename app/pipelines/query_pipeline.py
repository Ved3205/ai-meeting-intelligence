"""
app/pipelines/query_pipeline.py

Orchestrates the RAG question-answering workflow:

    question -> Query -> RetrievalService -> RetrievalResult[]
             -> LLMRequest -> LLMService -> LLMResponse
             -> Response

Design notes
------------
This module contains ONLY orchestration logic, mirroring the style of
`app.pipelines.video_pipeline.VideoPipeline`:

- Services are injected via the constructor, defaulting to real
  implementations, so the pipeline is unit-testable without Whisper,
  SentenceTransformer, Qdrant, or Ollama.
- Per SERVICES.md, `LLMService.generate_answer()` already obtains a QA
  prompt builder from `PromptFactory` and builds the prompt internally.
  This pipeline therefore does NOT touch `PromptFactory` or any prompt
  builder directly -- doing so would duplicate `LLMService`'s documented
  responsibility. The pipeline's job ends at constructing `LLMRequest`.
- Unlike `VideoPipeline`, this pipeline does NOT catch-and-convert
  service failures into a "failed" result object: `Response` has no
  success/error fields, and the calling layer (API route, CLI, etc.)
  needs the real exception, not a masked one. Failures are logged with
  context and re-raised.
- `Query` has no documented `meeting_id` field, and `RetrievalService`
  is documented as accepting only a `Query`. This pipeline therefore
  cannot filter retrieval by meeting -- that capability does not exist
  in the documented contract, so it isn't invented here.

Confidence
----------
No confidence-calculation utility is documented anywhere in this
project. The simplest defensible, clearly-stated approach is used:

    confidence = mean(RetrievalResult.score for all retrieved results)

clamped to [0.0, 1.0]. This is an explicit assumption, not a hidden
heuristic -- if the project later adds a real confidence utility,
`_compute_confidence` is the single place to swap it in.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from app.models.llm_request import LLMRequest
from app.models.query import Query
from app.models.response import Response
from app.models.retrieval_result import RetrievalResult
from app.models.retrieved_chunk import RetrievedChunk

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

# Simplest defensible confidence semantics: mean retrieval similarity
# score, clamped to a valid confidence range. See module docstring.
_MIN_CONFIDENCE = 0.0
_MAX_CONFIDENCE = 1.0

NO_CONTEXT_ANSWER = "No relevant information was found in the indexed meeting data."


class QueryPipeline:
    """
    Orchestrates the retrieval-augmented question-answering workflow.

    The pipeline contains no business logic: retrieval, embedding,
    prompt construction, and LLM generation are all delegated to
    existing services through their public APIs.
    """

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        llm_service: Optional[LLMService] = None,
    ) -> None:
        """
        Args:
            retrieval_service: Injected RetrievalService instance.
                Defaults to a real `RetrievalService()`.
            llm_service: Injected LLMService instance.
                Defaults to a real `LLMService()`.
        """
        self.retrieval_service = retrieval_service or RetrievalService()
        self.llm_service = llm_service or LLMService()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self,
        question: str,
        *,
        top_k: int = 5,
        score_threshold: float = 0.70,
    ) -> Response:
        """
        Execute the full query pipeline for a single question.

        Args:
            question: The user's natural-language question.
            top_k: Maximum number of chunks to retrieve.
            score_threshold: Minimum similarity score for a retrieved
                chunk to be considered relevant.

        Returns:
            A `Response` containing the grounded answer, the retrieved
            evidence, and a confidence score.

        Raises:
            ValueError: If `question`, `top_k`, or `score_threshold` are
                invalid.
            Exception: Any exception raised by `RetrievalService.retrieve()`
                or `LLMService.generate_answer()` propagates unchanged
                (logged with context first). This pipeline never converts
                a real failure into a fabricated answer.
        """
        logger.info("Starting query pipeline")

        self._validate_inputs(question, top_k, score_threshold)
        query = Query(question=question.strip(), top_k=top_k, score_threshold=score_threshold)
        logger.info(
            "Query validated (top_k=%d, score_threshold=%.2f)", top_k, score_threshold
        )

        retrieval_results = self._retrieve(query)
        logger.info("Retrieved %d chunks", len(retrieval_results))

        if not retrieval_results:
            logger.info("No relevant chunks found; returning controlled no-context response")
            return Response(
                answer=NO_CONTEXT_ANSWER,
                retrieved_chunks=[],
                confidence=_MIN_CONFIDENCE,
            )

        retrieved_chunks = [result.chunk for result in retrieval_results]

        logger.info("Generating grounded answer")
        llm_response = self._generate_answer(query.question, retrieved_chunks)

        confidence = self._compute_confidence(retrieval_results)
        logger.info("Query pipeline completed (confidence=%.2f)", confidence)

        return Response(
            answer=llm_response.answer,
            retrieved_chunks=retrieved_chunks,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_inputs(question: str, top_k: int, score_threshold: float) -> None:
        """
        Validate workflow-level inputs before constructing a Query or
        calling any service.

        Raises:
            ValueError: If any input is invalid.
        """
        if question is None or not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty, non-whitespace string")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError(f"top_k must be a positive integer, got {top_k!r}")
        if not isinstance(score_threshold, (int, float)) or isinstance(score_threshold, bool):
            raise ValueError(f"score_threshold must be a number, got {score_threshold!r}")
        if not (0.0 <= float(score_threshold) <= 1.0):
            raise ValueError(
                f"score_threshold must be between 0.0 and 1.0, got {score_threshold!r}"
            )

    def _retrieve(self, query: Query) -> List[RetrievalResult]:
        """Call RetrievalService.retrieve(), logging and re-raising on failure."""
        try:
            logger.info("Retrieving relevant chunks")
            return self.retrieval_service.retrieve(query)
        except Exception:
            logger.exception(
                "Retrieval failed (question=%r, top_k=%d, score_threshold=%.2f)",
                query.question,
                query.top_k,
                query.score_threshold,
            )
            raise

    def _generate_answer(self, question: str, retrieved_chunks: List[RetrievedChunk]):
        """Call LLMService.generate_answer(), logging and re-raising on failure."""
        llm_request = LLMRequest(question=question, retrieved_chunks=retrieved_chunks)
        try:
            return self.llm_service.generate_answer(llm_request)
        except Exception:
            logger.exception(
                "LLM answer generation failed (question=%r, retrieved_chunk_count=%d)",
                question,
                len(retrieved_chunks),
            )
            raise

    @staticmethod
    def _compute_confidence(retrieval_results: List[RetrievalResult]) -> float:
        """
        Compute a confidence score from retrieval similarity scores.

        ASSUMPTION (no existing confidence utility is documented in this
        project): confidence is the mean of all retrieved results'
        similarity scores, clamped to [0.0, 1.0].
        """
        scores = [result.score for result in retrieval_results]
        if not scores:
            return _MIN_CONFIDENCE
        average = sum(scores) / len(scores)
        return max(_MIN_CONFIDENCE, min(_MAX_CONFIDENCE, average))


# ---------------------------------------------------------------------------
# Convenience module-level function
# ---------------------------------------------------------------------------
def run_query_pipeline(question: str, **kwargs) -> Response:
    """
    Convenience wrapper that constructs a `QueryPipeline` with default,
    real service implementations and runs it once.

    Args:
        question: The user's natural-language question.
        **kwargs: Forwarded to `QueryPipeline.run` (top_k, score_threshold).

    Returns:
        The resulting `Response`.
    """
    pipeline = QueryPipeline()
    return pipeline.run(question, **kwargs)
