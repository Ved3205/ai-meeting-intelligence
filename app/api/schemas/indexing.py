"""
app/api/schemas/indexing.py

API-facing schemas for the bulk indexing endpoint, built from the real
`IndexingResult`/`IndexingEntry` fields (see app/pipelines/indexing_pipeline.py).
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class IndexingEntryResponse(BaseModel):
    """Outcome for one video within the batch."""

    video_path: str
    status: str = Field(..., description="'success', 'failed', or 'skipped_duplicate'.")
    meeting_id: Optional[str] = None
    total_chunks: Optional[int] = None
    error: Optional[str] = None
    elapsed_time: float


class IndexingResponse(BaseModel):
    """Response body for POST /api/v1/indexing."""

    total_videos: int
    successful_videos: int
    failed_videos: int
    skipped_videos: int
    entries: List[IndexingEntryResponse] = Field(default_factory=list)
    total_elapsed_time: float
