"""
app/api/routes/library.py

GET /api/v1/meetings              list indexed meetings
GET /api/v1/meetings/{meeting_id} one meeting
"""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_meeting_library
from app.api.schemas.library import MeetingInfoResponse, MeetingListResponse
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
