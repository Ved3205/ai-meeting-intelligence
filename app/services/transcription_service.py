"""
services/transcription_service.py

Business logic for speech-to-text transcription.

Responsibilities
----------------
1. Validate input audio.
2. Transcribe audio using Faster-Whisper.
3. Convert Whisper output into internal Transcript models.
4. Return Transcript.

This service DOES NOT:
- Save JSON
- Generate embeddings
- Store vectors
- Call LLMs
"""

from pathlib import Path

from app.core.model_manager import ModelManager

from app.models.audio import Audio
from app.models.transcript import Transcript
from app.models.transcript import TranscriptSegment

from app.utils.timer import Timer


class TranscriptionService:
    """
    Service responsible for converting an Audio object
    into a Transcript object.
    """

    def __init__(self):

        self.model = ModelManager.get_whisper_model()

    def transcribe(
        self,
        meeting_id: str,
        audio: Audio,
    ) -> Transcript:

        """
        Transcribe an audio file.
        Parameters
        ----------
        meeting_id : str
        audio : Audio
        Returns
        -------
        Transcript
        """

        self._validate_audio(audio)

        with Timer("Speech Transcription"):
            segments, info = self.model.transcribe(
                str(audio.file_path),
                beam_size=5,
                vad_filter=True,
                word_timestamps=False,
            )

        transcript_segments = self._convert_segments(segments)

        return Transcript(

            meeting_id=meeting_id,
            language=info.language,
            duration=audio.duration,
            segments=transcript_segments,
        )

    def _validate_audio(
        self,
        audio: Audio,
    ) -> None:
        """
        Validate audio before transcription.
        """

        if not audio.file_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio.file_path}"
            )

    def _convert_segments(
        self,
        whisper_segments,
    ) -> list[TranscriptSegment]:

        """
        Convert Faster-Whisper segments
        into TranscriptSegment models.
        """

        transcript_segments = []
        for idx, segment in enumerate(whisper_segments):
            transcript_segments.append(
                TranscriptSegment(
                    segment_id=idx,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    speaker=None,
                )
            )
        return transcript_segments