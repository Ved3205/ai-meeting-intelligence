"""
app/api/routes/indexing.py

    Client
      |
      v
POST /api/v1/indexing
      |
      v
save UploadFile[] -> Path[] under app.config.settings.UPLOAD_DIR
      |
      v
IndexingPipeline.run(paths)   <-- calls VideoPipeline once per video
                                   internally; this route NEVER calls
                                   VideoPipeline directly.
      |
      v
IndexingResponse
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.config import ApiConfig, get_api_config
from app.api.dependencies import get_indexing_pipeline
from app.api.schemas.indexing import IndexingEntryResponse, IndexingResponse
from app.config.settings import UPLOAD_DIR
from app.pipelines.indexing_pipeline import IndexingPipeline
from app.pipelines.video_pipeline import SUPPORTED_VIDEO_EXTENSIONS
from app.utils.file_utils import UnsupportedFileTypeError, UploadTooLargeError, save_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Indexing"])


@router.post(
    "/indexing",
    response_model=IndexingResponse,
    summary="Bulk-index multiple meeting videos",
    description="Saves the uploaded videos and processes them as a batch through the existing "
    "IndexingPipeline, which itself calls VideoPipeline once per video.",
    responses={
        413: {"description": "One of the uploaded files exceeds the configured maximum size."},
        500: {"description": "Unexpected error while processing the indexing batch."},
    },
)
async def bulk_index_meetings(
    files: List[UploadFile] = File(..., description="One or more meeting video files."),
    indexing_pipeline: IndexingPipeline = Depends(get_indexing_pipeline),
    api_config: ApiConfig = Depends(get_api_config),
) -> IndexingResponse:
    if not files:
        raise HTTPException(status_code=422, detail="At least one video file must be uploaded.")

    logger.info("Indexing request received: %d file(s)", len(files))

    saved_paths: List[Path] = []
    try:
        for upload in files:
            if not upload.filename:
                raise HTTPException(status_code=422, detail="Every uploaded file must have a filename.")
            try:
                dest_path = save_upload(
                    upload.file,
                    upload.filename,
                    UPLOAD_DIR,
                    SUPPORTED_VIDEO_EXTENSIONS,
                    max_size_bytes=api_config.max_upload_size_bytes,
                )
            except UnsupportedFileTypeError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            except UploadTooLargeError as exc:
                raise HTTPException(status_code=413, detail=str(exc)) from exc
            saved_paths.append(dest_path)
    finally:
        for upload in files:
            await upload.close()

    logger.info("Starting IndexingPipeline for %d saved file(s)", len(saved_paths))
    try:
        result = indexing_pipeline.run(saved_paths)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("IndexingPipeline failed")
        raise HTTPException(status_code=500, detail="Unable to process the indexing batch.")

    logger.info(
        "Indexing pipeline completed: total=%d successful=%d failed=%d",
        result.total_videos, result.successful_videos, result.failed_videos,
    )

    return IndexingResponse(
        total_videos=result.total_videos,
        successful_videos=result.successful_videos,
        failed_videos=result.failed_videos,
        skipped_videos=result.skipped_videos,
        entries=[
            IndexingEntryResponse(
                video_path=str(entry.video_path),
                status=entry.status,
                meeting_id=entry.meeting_id,
                total_chunks=entry.pipeline_result.total_chunks if entry.pipeline_result else None,
                error=entry.error,
                elapsed_time=entry.elapsed_time,
            )
            for entry in result.entries
        ],
        total_elapsed_time=result.total_elapsed_time,
    )
