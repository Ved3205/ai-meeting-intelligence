"""
app/api/schemas/meeting.py

API-facing schemas for the meeting upload endpoint. Deliberately NOT
the internal `PipelineResult`/`Meeting` domain models -- this is the
external HTTP contract, built from only the fields those models
actually expose.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class MeetingUploadResponse(BaseModel):
    """Result of uploading and processing one meeting video via VideoPipeline."""

    success: bool = Field(..., description="Whether VideoPipeline completed all stages successfully.")
    meeting_id: Optional[str] = Field(
        None, description="Identifier of the created meeting, if processing reached that stage."
    )
    title: Optional[str] = Field(None, description="Meeting title (defaults to the uploaded filename).")
    status: str = Field(..., description="'success' or 'failed'.")
    total_chunks: int = Field(0, description="Number of semantic chunks indexed into the vector store.")
    elapsed_time: float = Field(..., description="Seconds spent inside VideoPipeline.")
    errors: List[str] = Field(default_factory=list, description="Error messages if processing failed.")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings from VideoPipeline.")
