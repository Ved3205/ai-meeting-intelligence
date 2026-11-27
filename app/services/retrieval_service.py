"""
Retrieval Service

Handles semantic search using Qdrant.
"""

import re

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.config.settings import (
    COLLECTION_NAME,
    QDRANT_HOST,
    QDRANT_PORT,
)

from app.models.query import Query
from app.models.retrieval_result import RetrievalResult
from app.models.retrieved_chunk import RetrievedChunk

from app.vectorstore.shared_client import get_qdrant_client
from app.services.embedding_service import (
    EmbeddingService,
)


_STOPWORDS = {
    "the", "and", "what", "who", "did", "does", "was", "were", "are", "for",
    "about", "say", "said", "from", "this", "that", "with", "how", "why",
    "when", "where", "which", "give", "tell", "short", "summary", "meeting",
    "discussion", "anything", "have", "has", "had", "any", "all", "into",
}


def _query_terms(question: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", question.lower())
    return [w for w in dict.fromkeys(words) if len(w) > 2 and w not in _STOPWORDS]


class RetrievalService:

    def __init__(self):

        self.client = get_qdrant_client()

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

        query_filter = None
        if query.meeting_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="meeting_id",
                        match=MatchValue(value=query.meeting_id),
                    )
                ]
            )

        # Over-fetch so duplicates can be dropped and keywords can rerank.
        search_results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=query.top_k * 6,
            # score_threshold=query.score_threshold,
        )

        terms = _query_terms(query.question)
        seen = set()
        ranked = []
        for point in search_results.points:
            key = " ".join(point.payload["text"].split()).lower()
            if key in seen:
                continue
            seen.add(key)
            text = point.payload["text"].lower()
            hits = sum(1 for t in terms if t in text)
            boost = 0.3 * hits / len(terms) if terms else 0.0
            ranked.append((point.score + boost, point))
        ranked.sort(key=lambda r: r[0], reverse=True)

        retrieved = []
        for _, point in ranked[: query.top_k]:
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