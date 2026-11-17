"""
Retrieval Result Model
"""

from dataclasses import dataclass
from app.models.retrieved_chunk import RetrievedChunk

@dataclass(slots=True)
class RetrievalResult:
    """
    One search result returned from Qdrant.
    """
    chunk: RetrievedChunk
    score: float