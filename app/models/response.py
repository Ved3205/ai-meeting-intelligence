"""
Response Model
"""
from dataclasses import dataclass, field

from app.models.retrieved_chunk import RetrievedChunk

@dataclass(slots=True)
class Response:
    answer: str
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)
    confidence: float = 0.0