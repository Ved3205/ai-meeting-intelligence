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
QueryPipeline.run(question, top_k, score_threshold)  <-- unmodified
      |
      v
QueryResponse

See app/api/schemas/query.py's module docstring for the disclosed
meeting_id-scoping limitation. This route does NOT filter
`result.retrieved_chunks` by meeting_id after the fact -- per explicit
instruction, QueryPipeline's current behavior is left completely
unchanged; the limitation is only ever disclosed, never hidden or
silently "fixed" at the API layer.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_query_pipeline
from app.api.schemas.query import QueryRequest, QueryResponse, RetrievedChunkResponse
from app.pipelines.query_pipeline import QueryPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/meetings", tags=["Query"])


@router.post(
    "/{meeting_id}/query",
    response_model=QueryResponse,
    summary="Ask a question about indexed meetings",
    description="Runs the existing QueryPipeline. NOTE: retrieval is currently NOT scoped to "
    "meeting_id -- see the response's retrieval_scope_warning field and ROUTES.md.",
)
def query_meeting(
    meeting_id: str,
    request: QueryRequest,
    query_pipeline: QueryPipeline = Depends(get_query_pipeline),
) -> QueryResponse:
    logger.info("Query request received (meeting_id=%s)", meeting_id)

    try:
        result = query_pipeline.run(
            request.question, top_k=request.top_k, score_threshold=request.score_threshold
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
