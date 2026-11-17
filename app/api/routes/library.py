"""
app/api/routes/library.py

GET /api/v1/meetings              list indexed meetings
GET /api/v1/meetings/{meeting_id} one meeting
GET /api/v1/meetings/{meeting_id}/transcript  transcript by chunk
"""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_meeting_library
from app.api.schemas.library import (
    MeetingInfoResponse,
    MeetingListResponse,
    TranscriptResponse,
    TranscriptSegmentResponse,
)
from app.services.meeting_library_service import MeetingLibraryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/meetings", tags=["Meetings"])


@router.get("", response_model=MeetingListResponse, summary="List indexed meetings")
def list_meetings(library: MeetingLibraryService = Depends(get_meeting_library)) -> MeetingListResponse:
    try:
        meetings = library.list_meetings()
    except Exception:
        logger.exception("Listing meetings failed")
        raise HTTPException(status_code=500, detail="Unable to list meetings.")
    return MeetingListResponse(
        total=len(meetings),
        meetings=[MeetingInfoResponse(**asdict(m)) for m in meetings],
    )


@router.get(
    "/{meeting_id}",
    response_model=MeetingInfoResponse,
    summary="Get one indexed meeting",
    responses={404: {"description": "No indexed meeting with this id."}},
)
def get_meeting(
    meeting_id: str, library: MeetingLibraryService = Depends(get_meeting_library)
) -> MeetingInfoResponse:
    try:
        meeting = library.get_meeting(meeting_id)
    except Exception:
        logger.exception("Fetching meeting failed (meeting_id=%s)", meeting_id)
        raise HTTPException(status_code=500, detail="Unable to fetch the meeting.")
    if meeting is None:
        raise HTTPException(status_code=404, detail=f"Meeting not found: {meeting_id}")
    return MeetingInfoResponse(**asdict(meeting))


@router.get(
    "/{meeting_id}/transcript",
    response_model=TranscriptResponse,
    summary="Get a meeting transcript",
    description="The transcript is rebuilt from the indexed chunks, in order.",
    responses={404: {"description": "No indexed meeting with this id."}},
)
def get_transcript(
    meeting_id: str, library: MeetingLibraryService = Depends(get_meeting_library)
) -> TranscriptResponse:
    try:
        chunks = library.get_chunks(meeting_id)
    except Exception:
        logger.exception("Fetching transcript failed (meeting_id=%s)", meeting_id)
        raise HTTPException(status_code=500, detail="Unable to fetch the transcript.")
    if not chunks:
        raise HTTPException(status_code=404, detail=f"Meeting not found: {meeting_id}")
    return TranscriptResponse(
        meeting_id=meeting_id,
        segments=[
            TranscriptSegmentResponse(
                chunk_index=c["chunk_index"],
                start_time=c["start_time"],
                end_time=c["end_time"],
                text=c["text"],
            )
            for c in chunks
        ],
    )
