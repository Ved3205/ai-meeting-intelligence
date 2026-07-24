from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)


class MeetingVectorStore:

    def __init__(self):
        self.client = QdrantClient(
            host="localhost",
            port=6333,
        )

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
    ):
        collections = self.client.get_collections()

        existing = [
            c.name
            for c in collections.collections
        ]

        if collection_name in existing:
            print(f"Collection '{collection_name}' already exists.")
            return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        print(f"Collection '{collection_name}' created.")

    def upload_chunk(
        self,
        collection_name: str,
        chunk: dict,
        embedding: list[float],
    ):
        """
        Upload one chunk into Qdrant.
        """

        meeting_number = int(chunk["meeting_number"])
        chunk_number = int(chunk["chunk_id"].split("_")[1])

        numeric_id = meeting_number * 1000 + chunk_number

        point = PointStruct(
            id=numeric_id,
            vector=embedding,
            payload={
                "chunk_id": chunk["chunk_id"],
                "meeting_number": chunk["meeting_number"],
                "meeting_title": chunk["meeting_title"],
                "start": chunk["start"],
                "end": chunk["end"],
                "text": chunk["text"]
            }
        )

        self.client.upsert(
            collection_name=collection_name,
            points=[point],
            wait=True,
        )

        print(f"Uploaded chunk: {chunk['chunk_id']}")