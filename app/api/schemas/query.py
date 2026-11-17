"""
app/api/schemas/query.py

API-facing schemas for the meeting query endpoint.

KNOWN LIMITATION (disclosed to API consumers, not just in docs):
`QueryPipeline.run()` takes only `question`/`top_k`/`score_threshold`
-- there is no `meeting_id` parameter anywhere in its real,
unmodified implementation, and no meeting-scoping capability exists
in the underlying `Query`/`RetrievalService` contract. The
`{meeting_id}` path segment is accepted for a sane REST shape and is
echoed back in the response, but retrieval actually searches the
ENTIRE indexed corpus, not just that meeting. `QueryResponse.
retrieval_scope_warning` states this explicitly on every response so
it is never silently hidden from a consumer. See ROUTES.md.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

RETRIEVAL_SCOPE_WARNING = (
    "QueryPipeline currently retrieves from the entire indexed corpus, "
    "not scoped to this meeting_id. Meeting-scoped retrieval is a known "
    "limitation of the current pipeline -- see ROUTES.md."
)


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

    meeting_id: str = Field(..., description="The meeting_id from the request path (see limitation note).")
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    retrieved_chunks: List[RetrievedChunkResponse] = Field(default_factory=list)
    retrieval_scope_warning: str = Field(
        default=RETRIEVAL_SCOPE_WARNING,
        description="Always present: discloses that retrieval is not actually scoped to meeting_id.",
    )
