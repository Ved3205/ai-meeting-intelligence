"""
Transcript Model
"""

from dataclasses import dataclass, field

@dataclass(slots=True)
class TranscriptSegment:
    segment_id: int
    start: float
    end: float
    text: str
    speaker: str | None = None

@dataclass(slots=True)
class Transcript:
    meeting_id: str
    language: str
    duration: float
    segments: list[TranscriptSegment] = field(default_factory=list)