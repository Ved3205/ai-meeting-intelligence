"""
LLM Request Model
"""

from dataclasses import dataclass
from app.models.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class LLMRequest:
    """
    Represents everything the LLM needs to answer.
    """

    question: str
    retrieved_chunks: list[RetrievedChunk]