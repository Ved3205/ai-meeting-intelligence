"""
Meeting Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

@dataclass(slots=True)
class Meeting:
    meeting_id: str
    title: str
    video_path: Path
    created_at: datetime = field(default_factory=datetime.utcnow)
    uploaded_by: str | None = None
    workspace: str | None = None
    project: str | None = None
    status: str = "uploaded"