"""
services/chunking_service.py

Groups whole TranscriptSegments into chunks, keeping timestamps exact.
"""

from app.config.settings import (
    CHUNK_OVERLAP_SEGMENTS,
    MAX_WORDS_PER_CHUNK,
)

from app.models.chunk import Chunk
from app.models.transcript import Transcript


class ChunkingService:
    """
    Converts a Transcript into Chunk objects made of whole segments.
    """

    def __init__(self):

        self.max_words = MAX_WORDS_PER_CHUNK
        self.overlap = CHUNK_OVERLAP_SEGMENTS

    def chunk_transcript(
        self,
        transcript: Transcript,
    ) -> list[Chunk]:

        segments = [
            s for s in transcript.segments if s.text.strip()
        ]

        chunks = []
        start = 0

        while start < len(segments):

            end = start
            words = 0

            while end < len(segments):
                words += len(segments[end].text.split())
                end += 1
                if words >= self.max_words:
                    break

            group = segments[start:end]

            chunks.append(
                Chunk(
                    chunk_id=f"{transcript.meeting_id}_{len(chunks)}",
                    meeting_id=transcript.meeting_id,
                    chunk_index=len(chunks),
                    transcript_segments=group,
                    start_time=group[0].start,
                    end_time=group[-1].end,
                )
            )

            if end >= len(segments):
                break

            # Overlap by N segments but always move forward.
            start = max(end - self.overlap, start + 1)

        return chunks
