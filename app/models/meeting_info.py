from dataclasses import dataclass


@dataclass(slots=True)
class MeetingInfo:
    meeting_id: str
    title: str | None
    filename: str | None
    language: str | None
    total_chunks: int
    duration: float
    uploaded_at: str | None = None
