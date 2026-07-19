"""
Retrieved Chunk Model

Represents a chunk retrieved from the vector database.

Unlike Chunk, this class does not contain TranscriptSegment
objects because only the payload is stored in Qdrant.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class RetrievedChunk:
    """
    Represents one retrieved search result from Qdrant.
    """
    chunk_id: str
    meeting_id: str
    chunk_index: int
    text: str
    start_time: float
    end_time: float
    duration: float
    word_count: int
    token_count: int
    keywords: list[str]
    language: str | None = None
    title: str | None = None
    filename: str | None = None
    workspace: str | None = None
    project: str | None = None