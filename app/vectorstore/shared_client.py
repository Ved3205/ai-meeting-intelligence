"""One process-wide Qdrant client (embedded mode locks its folder)."""

from __future__ import annotations

import threading

from qdrant_client import QdrantClient

from app.config.settings import QDRANT_HOST, QDRANT_PATH, QDRANT_PORT

_lock = threading.Lock()
_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    with _lock:
        if _client is None:
            if QDRANT_PATH:
                _client = QdrantClient(path=QDRANT_PATH)
            else:
                _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        return _client
