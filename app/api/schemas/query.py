"""
app/api/schemas/query.py

API-facing schemas for the meeting query endpoint.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Request body for POST /api/v1/meetings/{meeting_id}/query."""

    question: str = Field(..., min_length=1, description="Natural-language question.")
    top_k: int = Field(5, gt=0, description="Maximum number of chunks to retrieve.")
    score_threshold: float = Field(
        0.70, ge=0.0, le=1.0, description="Minimum similarity score for a retrieved chunk."
    )


class RetrievedChunkResponse(BaseModel):
    """One piece of retrieved evidence backing the answer."""

    chunk_id: str
    meeting_id: str
    chunk_index: int
    text: str
    start_time: float
    end_time: float
    duration: float
    keywords: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    filename: Optional[str] = None


class QueryResponse(BaseModel):
    """Response body for POST /api/v1/meetings/{meeting_id}/query."""

    meeting_id: Optional[str] = Field(None, description="The meeting the query was scoped to, or null for all meetings.")
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    retrieved_chunks: List[RetrievedChunkResponse] = Field(default_factory=list)
