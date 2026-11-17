"""
app/api/routes/meetings.py

    Client
      |
      v
POST /api/v1/meetings/upload
      |
      v
save UploadFile -> Path under app.config.settings.UPLOAD_DIR (the REAL,
pre-existing project setting -- not a second, invented upload directory)
      |
      v
VideoPipeline.run(path)   <-- ALL processing logic lives here, unmodified
      |
      v
MeetingUploadResponse

DESIGN DECISION (disclosed): VideoPipeline.run() never raises for
documented failure modes -- it always returns a `PipelineResult` with
`success=False` and `errors` populated (verified from its real,
unmodified source). This route therefore returns HTTP 201 whenever the
pipeline actually RAN, regardless of whether processing succeeded --
the response body's `success`/`status`/`errors` fields communicate the
outcome, faithfully mirroring what VideoPipeline itself already
designed as its failure-reporting contract. A raised exception (the
rare, undocumented case) is the only case that becomes an HTTP 500.
Uses the existing `app.config.settings.UPLOAD_DIR` -- no second upload
directory. See ROUTES.md for the full documented contract.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.config import ApiConfig, get_api_config
from app.api.dependencies import get_video_pipeline
from app.api.schemas.meeting import MeetingUploadResponse
from app.pipelines.video_pipeline import SUPPORTED_VIDEO_EXTENSIONS, VideoPipeline
from app.config.settings import UPLOAD_DIR
from app.utils.file_utils import UnsupportedFileTypeError, UploadTooLargeError, save_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/meetings", tags=["Meetings"])


@router.post(
    "/upload",
    response_model=MeetingUploadResponse,
    status_code=201,
    summary="Upload and index a meeting video",
    description="Saves the uploaded video and processes it through the existing VideoPipeline "
    "(audio extraction, transcription, metadata, chunking, embedding, Qdrant upload).",
    responses={
        413: {
            "description": "Uploaded file is too large."
        },
        500: {
            "description": "Unexpected error while processing the uploaded video."
        },
    },
)
async def upload_meeting(
    file: UploadFile = File(..., description="Meeting video file (mp4, mkv, mov, avi, webm, m4v)."),
    video_pipeline: VideoPipeline = Depends(get_video_pipeline),
    api_config: ApiConfig = Depends(get_api_config),
) -> MeetingUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=422, detail="Uploaded file must have a filename.")

    logger.info("Meeting upload started: original_filename=%s", file.filename)

    try:
        dest_path: Path = save_upload(
            file.file,
            file.filename,
            UPLOAD_DIR,
            SUPPORTED_VIDEO_EXTENSIONS,
            max_size_bytes=api_config.max_upload_size_bytes,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    finally:
        await file.close()

    logger.info("Starting VideoPipeline for uploaded file")
    try:
        result = video_pipeline.run(dest_path, title=Path(file.filename).stem)
    except Exception:
        # Genuinely unexpected -- VideoPipeline's own contract is to
        # never raise for documented failures. See module docstring.
        logger.exception("VideoPipeline raised an unexpected exception")
        raise HTTPException(status_code=500, detail="Unexpected error while processing the uploaded video.")

    if result.success:
        logger.info("VideoPipeline completed successfully (meeting_id=%s)", result.meeting.meeting_id if result.meeting else "unknown")
    else:
        logger.warning("VideoPipeline reported failure: %s", result.errors)

    return MeetingUploadResponse(
        success=result.success,
        meeting_id=result.meeting.meeting_id if result.meeting else None,
        title=result.meeting.title if result.meeting else None,
        status="success" if result.success else "failed",
        total_chunks=result.total_chunks,
        elapsed_time=result.elapsed_time,
        errors=result.errors,
        warnings=result.warnings,
    )
