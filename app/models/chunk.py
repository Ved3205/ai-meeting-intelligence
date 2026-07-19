"""
Chunk Model
"""

from dataclasses import dataclass, field
import uuid
from app.models.metadata import Metadata
from app.models.transcript import TranscriptSegment
from qdrant_client.models import PointStruct

@dataclass(slots=True)
class Chunk:
    chunk_id: str
    meeting_id: str
    chunk_index: int
    transcript_segments: list[TranscriptSegment]
    start_time: float
    end_time: float
    token_count: int = 0
    embedding: list[float] | None = None
    metadata: Metadata | None = None
    keywords: list[str] = field(default_factory=list)
    # vector_id: str | None = None

    @property
    def vector_id(self) -> str:
        """
        Deterministic UUID used as the Qdrant Point ID.
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, self.chunk_id))


    def to_payload(self) -> dict:
        """
        Convert the chunk into a payload dictionary
        suitable for Qdrant.
        """

        payload = {
            "chunk_id": self.chunk_id,
            "meeting_id": self.meeting_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "word_count": self.word_count,
            "token_count": self.token_count,
            "keywords": self.keywords,
        }

        if self.metadata:

            payload.update({

                "title": self.metadata.title,

                "language": self.metadata.language,

                "filename": self.metadata.filename,

                "workspace": self.metadata.workspace,

                "project": self.metadata.project,

            })

        return payload


    def to_point(self) -> PointStruct:
        """
        Convert this Chunk into a Qdrant Point.
        """
        if self.embedding is None:
            raise ValueError(
                "Embedding has not been generated."
            )
        return PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, self.chunk_id)),
            vector=self.embedding,
            payload=self.to_payload(),
        )
    
    @property
    def text(self) -> str:
        return " ".join(
            segment.text
            for segment in self.transcript_segments
        )

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def speakers(self) -> list[str]:
        return sorted(
            {
                segment.speaker
                for segment in self.transcript_segments
                if segment.speaker
            }
        )