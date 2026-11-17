"""
services/vector_store_service.py

Handles storing and retrieving vectors from Qdrant.
"""
from qdrant_client.models import Filter
from app.models.retrieved_chunk import RetrievedChunk

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from app.config.settings import (
    COLLECTION_NAME,
    SIMILARITY_THRESHOLD,
    RETRIEVAL_LIMIT
)
from app.config.settings import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    VECTOR_SIZE,
)

from app.models.chunk import Chunk
class VectorStoreService:
    def __init__(self):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )
        self._create_collection()
    def _create_collection(self):
        collections = [
            c.name
            for c in self.client.get_collections().collections
        ]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            print("Collection Created.")
        else:
            print("Collection Already Exists.")
    def upload_chunk(
        self,
        chunk: Chunk,
    ):

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                chunk.to_point()
            ],
        )
    
    def upload_chunks(
        self,
        chunks: list[Chunk],
    ):
        points = [
            chunk.to_point()
            for chunk in chunks
            if chunk.embedding is not None
        ]

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(
            f"{len(points)} chunks uploaded."
        )


    def delete_meeting(
        self,
        meeting_id: str,
    ):
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "meeting_id",
                            "match": {
                                "value": meeting_id
                            }
                        }
                    ]
                }
            }
        )
    def count_vectors(self):
        info = self.client.get_collection(
            COLLECTION_NAME
        )
        return info.points_count

    def search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[RetrievedChunk]:

        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            limit=limit,
        )

        chunks = []

        for point in response.points:

            payload = point.payload

            chunks.append(
                RetrievedChunk(
                    chunk_id=payload["chunk_id"],
                    meeting_id=payload["meeting_id"],
                    chunk_index=payload["chunk_index"],
                    text=payload["text"],
                    start_time=payload["start_time"],
                    end_time=payload["end_time"],
                    duration=payload["duration"],
                    word_count=payload["word_count"],
                    token_count=payload["token_count"],
                    keywords=payload["keywords"],
                )
            )

        return chunks