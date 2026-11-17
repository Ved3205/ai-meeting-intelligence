"""
services/metadata_service.py

Creates metadata for a meeting using
Meeting, Audio and Transcript models.
"""

from pathlib import Path

from app.models.audio import Audio
from app.models.meeting import Meeting
from app.models.metadata import Metadata
from app.models.transcript import Transcript


class MetadataService:
    """
    Generates metadata for a meeting.

    This service combines information from
    Meeting, Audio and Transcript models
    into a Metadata object.
    """

    def generate(
        self,
        meeting: Meeting,
        audio: Audio,
        transcript: Transcript,
    ) -> Metadata:

        self._validate_models(
            meeting,
            audio,
            transcript,
        )

        return Metadata(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            filename=meeting.video_path.name,
            video_path=meeting.video_path,
            audio_path=audio.file_path,
            transcript_path=None,
            duration=audio.duration,
            language=transcript.language,
            total_segments=len(transcript.segments),
        )

    def _validate_models(
        self,
        meeting: Meeting,
        audio: Audio,
        transcript: Transcript,
    ) -> None:

        if meeting.meeting_id != transcript.meeting_id:

            raise ValueError(
                "Meeting ID mismatch between Meeting and Transcript."
            )

        if audio.duration <= 0:

            raise ValueError(
                "Audio duration must be greater than zero."
            )

        if len(transcript.segments) == 0:

            raise ValueError(
                "Transcript contains no segments."
            )