"""
services/chunking_service.py

Creates semantic chunks while preserving TranscriptSegment
objects and timestamps.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

from app.models.chunk import Chunk
from app.models.transcript import (
    Transcript,
    TranscriptSegment,
)


class ChunkingService:
    """
    Converts a Transcript into semantic Chunk objects.
    """

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "? ",
                "! ",
                " ",
                "",
            ],
            add_start_index=True,
        )

    def chunk_transcript(
        self,
        transcript: Transcript,
    ) -> list[Chunk]:

        text, segment_map = self._build_document(transcript)

        docs = self.splitter.create_documents([text])

        chunks = []

        for idx, doc in enumerate(docs):

            start = doc.metadata["start_index"]
            end = start + len(doc.page_content)

            chunk_segments = self._segments_for_range(
                segment_map,
                start,
                end,
            )

            if not chunk_segments:
                continue

            chunks.append(
                Chunk(
                    chunk_id=f"{transcript.meeting_id}_{idx}",
                    meeting_id=transcript.meeting_id,
                    chunk_index=idx,
                    transcript_segments=chunk_segments,
                    start_time=chunk_segments[0].start,
                    end_time=chunk_segments[-1].end,
                )
            )

        return chunks

    def _build_document(
        self,
        transcript: Transcript,
    ):

        parts = []
        mapping = []

        cursor = 0

        for segment in transcript.segments:

            text = segment.text.strip()

            start = cursor
            end = start + len(text)

            parts.append(text)

            mapping.append(
                {
                    "segment": segment,
                    "start": start,
                    "end": end,
                }
            )

            cursor = end + 1

        return "\n".join(parts), mapping

    def _segments_for_range(
        self,
        mapping,
        chunk_start,
        chunk_end,
    ):

        segments = []

        for item in mapping:

            if (
                item["end"] >= chunk_start
                and item["start"] <= chunk_end
            ):
                segments.append(item["segment"])

        return segments