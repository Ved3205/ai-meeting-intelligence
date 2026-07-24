"""
Retrieval Service

Handles semantic search using Qdrant.
"""

from qdrant_client import QdrantClient

from app.config.settings import (
    COLLECTION_NAME,
    QDRANT_HOST,
    QDRANT_PORT,
)

from app.models.query import Query
from app.models.retrieval_result import RetrievalResult
from app.models.retrieved_chunk import RetrievedChunk

from app.services.embedding_service import (
    EmbeddingService,
)


class RetrievalService:

    def __init__(self):

        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.embedding_service = EmbeddingService()

    def retrieve(
        self,
        query: Query,
    ) -> list[RetrievalResult]:

        query_vector = (
            self.embedding_service.embed_query(
                query.question
            )
        )

        search_results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=query.top_k,
            # score_threshold=query.score_threshold,
        )
        
        # print(len(search_results.points))
        retrieved = []
        for point in search_results.points:
            payload = point.payload
            chunk = RetrievedChunk(
                chunk_id=payload["chunk_id"],
                meeting_id=payload["meeting_id"],
                chunk_index=payload["chunk_index"],
                text=payload["text"],
                start_time=payload["start_time"],
                end_time=payload["end_time"],
                duration=payload["duration"],
                word_count=payload["word_count"],
                token_count=payload["token_count"],
                keywords=payload.get(
                    "keywords",
                    [],
                ),

                language=payload.get(
                    "language"
                ),

                title=payload.get(
                    "title"
                ),

                filename=payload.get(
                    "filename"
                ),

                workspace=payload.get(
                    "workspace"
                ),
                project=payload.get(
                    "project"
                ),
            )
            retrieved.append(
                RetrievalResult(
                    chunk=chunk,
                    score=point.score,
                )
            )
        return retrieved