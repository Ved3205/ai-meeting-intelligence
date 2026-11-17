"""
app/api/routes/jobs.py

POST /api/v1/uploads           save the video, start processing, return a job id
GET  /api/v1/uploads/{job_id}  poll the job status

The pipeline runs in a background thread, one video at a time because the
cached VideoPipeline is shared. POST /api/v1/meetings/upload still runs the
pipeline inside the request.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.api.config import ApiConfig, get_api_config
from app.api.dependencies import get_job_service, get_video_pipeline
from app.api.schemas.jobs import JobStatusResponse
from app.config.settings import UPLOAD_DIR
from app.pipelines.video_pipeline import SUPPORTED_VIDEO_EXTENSIONS, VideoPipeline
from app.services.job_service import COMPLETED, FAILED, PROCESSING, JobService
from app.utils.file_utils import UnsupportedFileTypeError, UploadTooLargeError, save_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/uploads", tags=["Uploads"])

_pipeline_lock = threading.Lock()


def _run_job(job_id: str, path: Path, title: str, pipeline: VideoPipeline, jobs: JobService) -> None:
    # Jobs wait here while another video is being processed.
    with _pipeline_lock:
        jobs.update(job_id, status=PROCESSING)
        started = time.perf_counter()
        try:
            result = pipeline.run(path, title=title, on_stage=lambda s: jobs.update(job_id, stage=s))
        except Exception:
            logger.exception("Upload job failed (job_id=%s)", job_id)
            jobs.update(
                job_id,
                status=FAILED,
                stage=None,
                elapsed_time=time.perf_counter() - started,
                errors=["Unexpected error while processing the uploaded video."],
            )
            return

    jobs.update(
        job_id,
        status=COMPLETED if result.success else FAILED,
        stage=None,
        meeting_id=result.meeting.meeting_id if result.meeting else None,
        title=result.meeting.title if result.meeting else title,
        total_chunks=result.total_chunks,
        elapsed_time=result.elapsed_time,
        errors=result.errors,
        warnings=result.warnings,
    )


@router.post(
    "",
    response_model=JobStatusResponse,
    status_code=202,
    summary="Upload a meeting video and process it in the background",
    responses={
        413: {"description": "Uploaded file is too large."},
        422: {"description": "Missing filename or unsupported file type."},
    },
)
def start_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Meeting video file (mp4, mkv, mov, avi, webm, m4v)."),
    pipeline: VideoPipeline = Depends(get_video_pipeline),
    jobs: JobService = Depends(get_job_service),
    api_config: ApiConfig = Depends(get_api_config),
) -> JobStatusResponse:
    if not file.filename:
        raise HTTPException(status_code=422, detail="Uploaded file must have a filename.")

    try:
        path = save_upload(
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
        file.file.close()

    job = jobs.create(file.filename)
    background_tasks.add_task(_run_job, job.job_id, path, Path(file.filename).stem, pipeline, jobs)
    logger.info("Upload job queued (job_id=%s)", job.job_id)
    return JobStatusResponse(**asdict(job))


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get the status of an upload job",
    responses={404: {"description": "Unknown job id."}},
)
def get_upload_status(job_id: str, jobs: JobService = Depends(get_job_service)) -> JobStatusResponse:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return JobStatusResponse(**asdict(job))
