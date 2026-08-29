"""
app/api/schemas/summary.py

API-facing schemas for the meeting summary endpoint. No request body
is needed -- `SummaryPipeline.run()` takes only `meeting_id`, which
comes from the URL path.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ActionItemResponse(BaseModel):
    """One action item extracted from the meeting. Owner/deadline are
    omitted (null) rather than fabricated when not stated in the meeting."""

    description: str
    owner: Optional[str] = None
    deadline: Optional[str] = None


class SummaryResponse(BaseModel):
    """Response body for POST /api/v1/meetings/{meeting_id}/summary."""

    meeting_id: str
    title: str
    summary: str
    keywords: List[str] = Field(default_factory=list)
    action_items: List[ActionItemResponse] = Field(default_factory=list)
    chunk_count: int = Field(..., description="Number of indexed chunks the summary was grounded in.")
    elapsed_time: float
