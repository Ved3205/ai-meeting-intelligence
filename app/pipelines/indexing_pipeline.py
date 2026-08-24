"""
app/pipelines/indexing_pipeline.py

Batch orchestrator over the existing `VideoPipeline`:

    IndexingPipeline
          |
          v
    for each video path:
          |
          v
    VideoPipeline.run(video_path)  -- unmodified, reused as-is
          |
          v
    IndexingEntry (wraps the real PipelineResult, never reconstructs it)
          |
          v
    IndexingResult (batch rollup)

IndexingPipeline contains no video-processing logic whatsoever: no
audio extraction, no transcription, no chunking, no embedding, no
Qdrant access, no prompt construction, no LLM calls. Its only job is
to call `VideoPipeline.run()` once per video, track outcomes, and keep
going when an individual video fails.

Two judgment calls made here are NOT backed by any real PIPELINES.md
(none was provided beyond task instructions -- see the accompanying
explanation): directory expansion and in-batch duplicate-path
detection. Both are implemented as narrow, clearly-flagged, opt-out-able
conveniences rather than assumed architecture -- see `run()`'s docstring.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Union

from app.models.pipeline_result import PipelineResult
from app.pipelines.video_pipeline import SUPPORTED_VIDEO_EXTENSIONS, VideoPipeline

logger = logging.getLogger(__name__)

PathLike = Union[str, Path]


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------
@dataclass
class IndexingEntry:
    """
    Outcome for one video within a batch.

    `pipeline_result` is the REAL, unmodified `PipelineResult` object
    returned by `VideoPipeline.run()` -- never reconstructed or
    summarized. It is `None` only in the rare case where an exception
    escaped `VideoPipeline.run()` itself (see module docstring) or when
    `status == "skipped_duplicate"` (the video was never actually run).
    """

    video_path: Path
    status: str  # "success" | "failed" | "skipped_duplicate"
    pipeline_result: Optional[PipelineResult] = None
    error: Optional[str] = None
    elapsed_time: float = 0.0

    @property
    def meeting_id(self) -> Optional[str]:
        if self.pipeline_result and self.pipeline_result.meeting:
            return self.pipeline_result.meeting.meeting_id
        return None


@dataclass
class IndexingResult:
    """
    Batch-level rollup of an IndexingPipeline run.

    No equivalent model exists in MODELS.md, so this is the smallest
    appropriate model for the batch statistics plus per-video entries.
    """

    total_videos: int
    successful_videos: int
    failed_videos: int
    skipped_videos: int
    entries: List[IndexingEntry] = field(default_factory=list)
    total_elapsed_time: float = 0.0

    @property
    def successes(self) -> List[IndexingEntry]:
        return [e for e in self.entries if e.status == "success"]

    @property
    def failures(self) -> List[IndexingEntry]:
        return [e for e in self.entries if e.status == "failed"]

    def summary(self) -> str:
        return (
            f"total={self.total_videos} successful={self.successful_videos} "
            f"failed={self.failed_videos} skipped={self.skipped_videos} "
            f"elapsed={self.total_elapsed_time:.2f}s"
        )


# ---------------------------------------------------------------------------
# Indexing pipeline
# ---------------------------------------------------------------------------
class IndexingPipeline:
    """
    Batch orchestrator that repeatedly invokes an existing `VideoPipeline`
    instance, one call per video, continuing past individual failures.
    """

    def __init__(self, video_pipeline: Optional[VideoPipeline] = None) -> None:
        """
        Args:
            video_pipeline: Injected `VideoPipeline` instance. Defaults to
                a real `VideoPipeline()`. This is the ONLY dependency --
                IndexingPipeline never talks to any other service.
        """
        self.video_pipeline = video_pipeline or VideoPipeline()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self,
        video_paths: Sequence[PathLike],
        *,
        resolve_directories: bool = True,
    ) -> IndexingResult:
        """
        Process a batch of videos by calling `VideoPipeline.run()` once
        per video, sequentially, continuing past individual failures.

        Args:
            video_paths: One or more video paths (str or Path). An entry
                that is a directory is expanded (see `resolve_directories`)
                unless directory expansion is disabled.
            resolve_directories: If True (default), any entry in
                `video_paths` that is an existing directory is expanded,
                non-recursively, into the video files it directly
                contains (matched against
                `VideoPipeline.SUPPORTED_VIDEO_EXTENSIONS` -- no second,
                conflicting extension list is introduced). This is a
                convenience feature, not a documented requirement (no
                real PIPELINES.md was available to confirm directory
                support); set this to False to disable it and treat
                every entry strictly as a file path, letting
                `VideoPipeline` reject anything that isn't.

        Returns:
            An `IndexingResult` with per-video outcomes and batch totals.

        Raises:
            ValueError: If `video_paths` is empty, `None`, or contains a
                non-path-like item. Individual videos that don't exist or
                have unsupported extensions are NOT rejected here -- they
                are forwarded to `VideoPipeline.run()`, which already
                performs that validation and reports it in the returned
                `PipelineResult`, so that validation is never duplicated.
        """
        start_time = time.perf_counter()
        logger.info("=" * 42)
        logger.info("INDEXING PIPELINE")
        logger.info("=" * 42)

        self._validate_batch_input(video_paths)

        resolved = self._resolve_inputs(video_paths, resolve_directories=resolve_directories)
        ordered, duplicate_paths = self._deduplicate_and_sort(resolved)

        logger.info("Found %d video(s).", len(ordered))

        entries: List[IndexingEntry] = []
        successful = 0
        failed = 0

        total = len(ordered)
        for index, video_path in enumerate(ordered, start=1):
            logger.info("[%d/%d] Processing: %s", index, total, video_path)
            entry = self._process_one(video_path, index, total)
            entries.append(entry)
            if entry.status == "success":
                successful += 1
            else:
                failed += 1

        skipped = 0
        for dup_path in duplicate_paths:
            logger.info(
                "Skipping duplicate path within this batch (already processed above): %s",
                dup_path,
            )
            entries.append(
                IndexingEntry(
                    video_path=dup_path,
                    status="skipped_duplicate",
                    pipeline_result=None,
                    error="Duplicate path within this batch; already processed once.",
                    elapsed_time=0.0,
                )
            )
            skipped += 1

        total_elapsed = time.perf_counter() - start_time

        logger.info("=" * 42)
        logger.info("INDEXING COMPLETE")
        logger.info("=" * 42)
        logger.info(
            "Total: %d  Successful: %d  Failed: %d  Skipped: %d  Time: %.2fs",
            len(entries), successful, failed, skipped, total_elapsed,
        )

        return IndexingResult(
            total_videos=len(entries),
            successful_videos=successful,
            failed_videos=failed,
            skipped_videos=skipped,
            entries=entries,
            total_elapsed_time=total_elapsed,
        )

    # ------------------------------------------------------------------
    # Per-video processing
    # ------------------------------------------------------------------
    def _process_one(self, video_path: Path, index: int, total: int) -> IndexingEntry:
        """
        Call `VideoPipeline.run()` for a single video, wrapped in
        try/except purely as a safety net for the rare case where an
        exception escapes `VideoPipeline.run()` before its own internal
        error handling begins (see module docstring). The exception is
        never swallowed -- it is recorded on the entry and logged, and
        processing continues with the next video.
        """
        video_start = time.perf_counter()
        try:
            pipeline_result = self.video_pipeline.run(video_path)
        except Exception as exc:
            elapsed = time.perf_counter() - video_start
            logger.exception("[%d/%d] FAILED (unexpected exception): %s", index, total, video_path)
            return IndexingEntry(
                video_path=video_path,
                status="failed",
                pipeline_result=None,
                error=f"{type(exc).__name__}: {exc}",
                elapsed_time=elapsed,
            )

        elapsed = time.perf_counter() - video_start

        if pipeline_result.success:
            meeting_id = pipeline_result.meeting.meeting_id if pipeline_result.meeting else "unknown"
            logger.info("[%d/%d] SUCCESS -- Meeting ID: %s", index, total, meeting_id)
            return IndexingEntry(
                video_path=video_path,
                status="success",
                pipeline_result=pipeline_result,
                error=None,
                elapsed_time=elapsed,
            )

        error_message = "; ".join(pipeline_result.errors) or "Unknown failure"
        logger.warning("[%d/%d] FAILED -- %s", index, total, error_message)
        return IndexingEntry(
            video_path=video_path,
            status="failed",
            pipeline_result=pipeline_result,
            error=error_message,
            elapsed_time=elapsed,
        )

    # ------------------------------------------------------------------
    # Batch-level validation and resolution (NOT VideoPipeline's job)
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_batch_input(video_paths: Sequence[PathLike]) -> None:
        """
        Batch-level validation only: is the collection present, non-empty,
        and made of path-like items? Per-file existence/extension
        validation is deliberately NOT duplicated here -- that is
        `VideoPipeline`'s documented responsibility.
        """
        if video_paths is None:
            raise ValueError("video_paths must not be None")
        if not isinstance(video_paths, (list, tuple)):
            raise ValueError(
                f"video_paths must be a list or tuple of str/Path, got {type(video_paths).__name__}"
            )
        if len(video_paths) == 0:
            raise ValueError("video_paths must not be empty")
        for item in video_paths:
            if not isinstance(item, (str, Path)):
                raise ValueError(
                    f"Each item in video_paths must be a str or Path, got {type(item).__name__}: {item!r}"
                )

    @staticmethod
    def _resolve_inputs(
        video_paths: Sequence[PathLike], *, resolve_directories: bool
    ) -> List[Path]:
        """
        Normalize every item to a `Path`, expanding directories (if
        enabled) into their directly-contained supported video files.
        Non-recursive by design -- see `run()`'s docstring.
        """
        resolved: List[Path] = []
        for item in video_paths:
            path = Path(item)
            if resolve_directories and path.is_dir():
                found = sorted(
                    f for f in path.iterdir()
                    if f.is_file() and f.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS
                )
                if not found:
                    logger.warning("Directory contains no supported video files: %s", path)
                resolved.extend(found)
            else:
                resolved.append(path)
        return resolved

    @staticmethod
    def _deduplicate_and_sort(paths: List[Path]) -> tuple[List[Path], List[Path]]:
        """
        Remove exact-path duplicates (first occurrence wins) and return a
        deterministically sorted list, plus the list of duplicate paths
        that were skipped.

        This is intentionally shallow: it compares `Path` values as given
        (after `Path()` normalization), NOT resolved/canonicalized
        filesystem identity. Two different relative paths or a symlink
        pointing at the same file are NOT detected as duplicates -- doing
        so would require inventing an undocumented "same meeting" concept,
        which the task explicitly prohibits guessing at.
        """
        seen: set = set()
        unique: List[Path] = []
        duplicates: List[Path] = []
        for path in paths:
            if path in seen:
                duplicates.append(path)
                continue
            seen.add(path)
            unique.append(path)

        ordered = sorted(unique, key=lambda p: str(p))
        return ordered, duplicates


# ---------------------------------------------------------------------------
# Convenience module-level function
# ---------------------------------------------------------------------------
def run_indexing_pipeline(video_paths: Sequence[PathLike], **kwargs) -> IndexingResult:
    """
    Convenience wrapper that constructs an `IndexingPipeline` with a
    default, real `VideoPipeline` and runs it once.

    Args:
        video_paths: One or more video paths.
        **kwargs: Forwarded to `IndexingPipeline.run` (resolve_directories).

    Returns:
        The resulting `IndexingResult`.
    """
    pipeline = IndexingPipeline()
    return pipeline.run(video_paths, **kwargs)
