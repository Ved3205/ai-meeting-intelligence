"""
app/api/schemas/jobs.py

API-facing schemas for background upload jobs.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class JobStatusResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="'queued', 'processing', 'completed' or 'failed'.")
    stage: Optional[str] = Field(None, description="Current pipeline stage while processing.")
    filename: str
    meeting_id: Optional[str] = None
    title: Optional[str] = None
    total_chunks: int = 0
    elapsed_time: float = 0.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str
