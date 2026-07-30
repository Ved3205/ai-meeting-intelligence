"""
Prompt Formatter

Contains reusable formatting utilities for prompt builders.
"""

from __future__ import annotations

from app.models.metadata import Metadata
from app.models.retrieved_chunk import RetrievedChunk


class PromptFormatter:
    """
    Shared formatter used by all prompt builders.
    """

    # ==========================================================
    # Retrieved Chunks
    # ==========================================================

    @staticmethod
    def format_retrieved_chunks(
        chunks: list[RetrievedChunk],
    ) -> str:

        if not chunks:
            return "No retrieved context."

        sections = []

        for chunk in chunks:

            sections.append(
                f"""
Chunk ID : {chunk.chunk_id}

Meeting ID : {chunk.meeting_id}

Timestamp : {chunk.start_time:.2f}s → {chunk.end_time:.2f}s

Content

{chunk.text}
"""
            )

        return "\n\n".join(sections)

    # ==========================================================
    # Transcript
    # ==========================================================

    @staticmethod
    def format_transcript(
        transcript: str | None,
    ) -> str:

        if transcript is None:
            return ""

        return transcript.strip()

    # ==========================================================
    # Metadata
    # ==========================================================

    @staticmethod
    def format_metadata(
        metadata: Metadata | None,
    ) -> str:

        if metadata is None:
            return "No metadata available."

        lines = []

        for key, value in vars(metadata).items():

            lines.append(f"{key}: {value}")

        return "\n".join(lines)

    # ==========================================================
    # Timestamp
    # ==========================================================

    @staticmethod
    def format_timestamp(
        start: float,
        end: float,
    ) -> str:

        return f"{start:.2f}s → {end:.2f}s"

    # ==========================================================
    # Generic Section
    # ==========================================================

    @staticmethod
    def section(
        title: str,
        content: str,
    ) -> str:

        return (
            f"{title.upper()}\n"
            f"{'-'*len(title)}\n"
            f"{content.strip()}\n"
        )