"""
Prompt Request Model

Represents all information that may be required by
different prompt builders.
"""

from dataclasses import dataclass, field

from app.models.metadata import Metadata
from app.models.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class PromptRequest:
    """
    Generic request object for prompt builders.

    Not every field will be used by every prompt.
    """

    # ==================================================
    # User Question
    # ==================================================

    question: str | None = None

    # ==================================================
    # Retrieved Context
    # ==================================================

    retrieved_chunks: list[RetrievedChunk] = field(
        default_factory=list
    )

    # ==================================================
    # Full Transcript
    # ==================================================

    transcript: str | None = None

    # ==================================================
    # Meeting Metadata
    # ==================================================

    metadata: Metadata | None = None