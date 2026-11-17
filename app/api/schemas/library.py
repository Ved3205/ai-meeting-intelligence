"""
app/api/schemas/library.py

API-facing schemas for listing and reading indexed meetings.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class MeetingInfoResponse(BaseModel):
    meeting_id: str
    title: Optional[str] = None
    filename: Optional[str] = None
    language: Optional[str] = None
    total_chunks: int
    duration: float = Field(..., description="Meeting length in seconds, taken from the last chunk.")
    uploaded_at: Optional[str] = Field(None, description="ISO timestamp, null for meetings indexed before it was stored.")


class MeetingListResponse(BaseModel):
    total: int
    meetings: List[MeetingInfoResponse] = Field(default_factory=list)
