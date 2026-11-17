"""
app/api/routes/summary.py

    Client
      |
      v
POST /api/v1/meetings/{meeting_id}/summary
      |
      v
SummaryPipeline.run(meeting_id)   <-- unmodified; does its own
                                       retrieval/prompt/LLM orchestration
      |
      v
SummaryResponse
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_summary_pipeline
from app.api.schemas.summary import ActionItemResponse, SummaryResponse
from app.pipelines.summary_pipeline import (
    EmptyMeetingContentError,
    MeetingNotFoundError,
    SummaryPipeline,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/meetings", tags=["Summary"])


@router.post(
    "/{meeting_id}/summary",
    response_model=SummaryResponse,
    summary="Generate meeting summary, title, keywords, and action items",
    description="Runs the existing SummaryPipeline against an already-indexed meeting.",
    responses={
        404: {
            "description": "No indexed content found for this meeting_id."
        },
        500: {
            "description": "Unexpected error while generating the summary."
        },
    },
)
def summarize_meeting(
    meeting_id: str,
    summary_pipeline: SummaryPipeline = Depends(get_summary_pipeline),
) -> SummaryResponse:
    logger.info("Summary request received (meeting_id=%s)", meeting_id)

    try:
        result = summary_pipeline.run(meeting_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MeetingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EmptyMeetingContentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("SummaryPipeline failed (meeting_id=%s)", meeting_id)
        raise HTTPException(status_code=500, detail="Unable to generate meeting summary.")

    logger.info("Summary pipeline completed (meeting_id=%s)", meeting_id)

    return SummaryResponse(
        meeting_id=result.meeting_id,
        title=result.title,
        summary=result.summary,
        keywords=result.keywords,
        action_items=[
            ActionItemResponse(description=item["description"], owner=item.get("owner"), deadline=item.get("deadline"))
            for item in result.action_items
        ],
        chunk_count=result.chunk_count,
        elapsed_time=result.elapsed_time,
    )
