"""
app/api/routes/query.py

    Client
      |
      v
POST /api/v1/meetings/{meeting_id}/query
      |
      v
QueryRequest
      |
      v
QueryPipeline.run(question, top_k, score_threshold, meeting_id)
      |
      v
QueryResponse

POST /api/v1/query does the same without a meeting_id and searches
every indexed meeting.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_query_pipeline
from app.api.schemas.query import QueryRequest, QueryResponse, RetrievedChunkResponse
from app.pipelines.query_pipeline import QueryPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Query"])


def _run_query(
    request: QueryRequest,
    query_pipeline: QueryPipeline,
    meeting_id: Optional[str],
) -> QueryResponse:
    try:
        result = query_pipeline.run(
            request.question,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            meeting_id=meeting_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("QueryPipeline failed (meeting_id=%s)", meeting_id)
        raise HTTPException(status_code=500, detail="Unable to process the query.")

    logger.info("Query pipeline completed (meeting_id=%s, confidence=%.2f)", meeting_id, result.confidence)

    return QueryResponse(
        meeting_id=meeting_id,
        answer=result.answer,
        confidence=result.confidence,
        retrieved_chunks=[
            RetrievedChunkResponse(
                chunk_id=chunk.chunk_id,
                meeting_id=chunk.meeting_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                start_time=chunk.start_time,
                end_time=chunk.end_time,
                duration=chunk.duration,
                keywords=chunk.keywords,
                title=chunk.title,
                filename=chunk.filename,
            )
            for chunk in result.retrieved_chunks
        ],
    )


@router.post(
    "/meetings/{meeting_id}/query",
    response_model=QueryResponse,
    summary="Ask a question about one meeting",
    description="Runs the QueryPipeline with retrieval limited to the given meeting.",
)
def query_meeting(
    meeting_id: str,
    request: QueryRequest,
    query_pipeline: QueryPipeline = Depends(get_query_pipeline),
) -> QueryResponse:
    logger.info("Query request received (meeting_id=%s)", meeting_id)
    return _run_query(request, query_pipeline, meeting_id)


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Ask a question across all meetings",
    description="Runs the QueryPipeline over every indexed meeting.",
)
def query_all_meetings(
    request: QueryRequest,
    query_pipeline: QueryPipeline = Depends(get_query_pipeline),
) -> QueryResponse:
    logger.info("Query request received (all meetings)")
    return _run_query(request, query_pipeline, None)
