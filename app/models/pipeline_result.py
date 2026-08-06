"""
app/models/pipeline_result.py

Represents the outcome of running an end-to-end ingestion pipeline
(e.g. VideoPipeline). Captures every intermediate artifact produced
along the way so callers (APIs, CLIs, tests) can inspect partial
progress even when the pipeline fails part-way through.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Imported only for type checking to avoid unnecessary runtime
    # coupling / circular imports between model modules.
    from app.models.meeting import Meeting
    from app.models.audio import Audio
    from app.models.transcript import Transcript
    from app.models.metadata import Metadata
    from app.models.chunk import Chunk


@dataclass
class PipelineResult:
    """
    Structured result object returned by ingestion pipelines.

    Attributes:
        success: Whether the pipeline completed every stage without error.
        meeting: The Meeting record created for this run, if reached.
        audio: The extracted Audio artifact, if reached.
        transcript: The generated Transcript, if reached.
        metadata: The generated Metadata, if reached.
        chunks: The list of Chunk objects produced (embedded, if embedding
            succeeded).
        total_chunks: Convenience count of `chunks`.
        elapsed_time: Total wall-clock time spent in the pipeline, in seconds.
        errors: Human-readable error messages describing any failures.
        warnings: Non-fatal issues encountered during the run.
    """

    success: bool
    meeting: Optional["Meeting"] = None
    audio: Optional["Audio"] = None
    transcript: Optional["Transcript"] = None
    metadata: Optional["Metadata"] = None
    chunks: List["Chunk"] = field(default_factory=list)
    total_chunks: int = 0
    elapsed_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Keep total_chunks consistent with the chunks list unless the
        # caller explicitly overrode it (e.g. before chunks were embedded).
        if self.chunks and self.total_chunks == 0:
            self.total_chunks = len(self.chunks)

    def summary(self) -> str:
        """Return a short, human-readable one-line summary of the result."""
        status = "SUCCESS" if self.success else "FAILED"
        meeting_id = self.meeting.meeting_id if self.meeting else "unknown"
        return (
            f"[{status}] meeting={meeting_id} "
            f"chunks={self.total_chunks} "
            f"elapsed={self.elapsed_time:.2f}s "
            f"errors={len(self.errors)} warnings={len(self.warnings)}"
        )
