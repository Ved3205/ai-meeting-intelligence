"""
services/chunking_service.py

Converts Transcript into semantic chunks.

Responsibilities
----------------
1. Receive Transcript
2. Split transcript into chunks
3. Preserve timestamps
4. Return Chunk models
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)

from app.models.chunk import Chunk
from app.models.transcript import Transcript

class ChunkingService:
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
                ""
            ],
        )
    def chunk_transcript(
        self,
        transcript: Transcript,
    ) -> list[Chunk]:
        """
        Convert transcript into Chunk objects.
        """
        transcript_text = self._build_text(transcript)
        chunk_texts = self.splitter.split_text(transcript_text)
        chunks = []
        for index, text in enumerate(chunk_texts):
            chunks.append(
                Chunk(
                    chunk_id=f"{transcript.meeting_id}_{index}",
                    meeting_id=transcript.meeting_id,
                    chunk_index=index,
                    text=text,
                    start_time=None,
                    end_time=None,
                )
            )
        return chunks
    def _build_text(
        self,
        transcript: Transcript,
    ) -> str:

        """
        Merge transcript segments into one document.
        """
        return "\n".join(
            segment.text
            for segment in transcript.segments
        )