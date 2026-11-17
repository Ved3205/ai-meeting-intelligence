"""
services/job_service.py

In-memory tracking of background upload jobs.
"""

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

QUEUED = "queued"
PROCESSING = "processing"
COMPLETED = "completed"
FAILED = "failed"


@dataclass
class Job:
    job_id: str
    filename: str
    status: str = QUEUED
    stage: str | None = None
    meeting_id: str | None = None
    title: str | None = None
    total_chunks: int = 0
    elapsed_time: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class JobService:

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, filename: str) -> Job:
        job = Job(job_id=str(uuid.uuid4()), filename=filename)
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **fields) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in fields.items():
                setattr(job, key, value)
