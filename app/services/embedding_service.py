"""
services/embedding_service.py

Generates vector embeddings for transcript chunks.
"""

from sentence_transformers import SentenceTransformer

from app.core.model_manager import ModelManager
from app.models.chunk import Chunk
from app.config.settings import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_NORMALIZE,
)

class EmbeddingService:
    """
    Generates embeddings for transcript chunks.
    """

    def __init__(self):

        self.model: SentenceTransformer = (
            ModelManager.get_embedding_model()
        )

    def embed_chunk(
        self,
        chunk: Chunk,
    ) -> Chunk:
        """
        Generate embedding for a single chunk.
        """

        embedding = self.model.encode(
            chunk.text,
            normalize_embeddings=EMBEDDING_NORMALIZE,
            convert_to_numpy=True,
        )

        chunk.embedding = embedding.tolist()

        chunk.token_count = self._estimate_tokens(chunk.text)

        return chunk

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:
        """
        Batch embedding generation.
        """

        texts = [chunk.text for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=EMBEDDING_NORMALIZE,
            convert_to_numpy=True,
            batch_size=EMBEDDING_BATCH_SIZE,
        )

        for chunk, embedding in zip(chunks, embeddings):

            chunk.embedding = embedding.tolist()

            chunk.token_count = self._estimate_tokens(
                chunk.text
            )

        return chunks

    def embed_query(
        self,
        question: str,
    ) -> list[float]:
        embedding = self.model.encode(
            question,
            normalize_embeddings=EMBEDDING_NORMALIZE,
            convert_to_numpy=True,
        )
        return embedding.tolist()

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Rough token estimation.
        """

        return int(len(text.split()) * 1.3)