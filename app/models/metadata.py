"""
models/metadata.py

Metadata Model

Stores descriptive information about a meeting.
This model is used for searching, filtering,
analytics, and future SaaS features.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class Metadata:
    """
    Metadata describing a meeting.
    """

    # =====================================================
    # Meeting Information
    # =====================================================

    meeting_id: str
    title: str
    filename: str
    # =====================================================
    # Paths
    # =====================================================
    video_path: Path
    audio_path: Path | None = None
    transcript_path: Path | None = None
    # =====================================================
    # Audio / Transcript Information
    # =====================================================

    duration: float = 0.0
    language: str = "unknown"
    total_segments: int = 0
    # =====================================================
    # Upload Information
    # =====================================================

    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    uploaded_by: str | None = None
    # =====================================================
    # Future SaaS Features
    # =====================================================

    tags: list[str] = field(default_factory=list)
    workspace: str | None = None
    project: str | None = None
    participants: list[str] = field(default_factory=list)