"""
app/api/config.py

API-layer-only configuration. This is deliberately SEPARATE from
`app/settings.py` (the real, pre-existing project settings module) and
does not duplicate or override anything defined there.

`app/settings.py` already defines `UPLOAD_DIR` and every pipeline/
service-level constant (WHISPER_*, CHUNK_*, EMBEDDING_*, QDRANT_*,
LLM_*, TOP_K, RETRIEVAL_LIMIT, SIMILARITY_THRESHOLD) -- routes import
those directly from `app.config.settings`, exactly as `SERVICES.md` shows the
existing services doing (bare top-level constant imports, no settings
object). This module only adds the handful of values that are purely
an HTTP-layer concern and have no equivalent in the real settings.py:
API title/version for OpenAPI, CORS origins, and an upload size cap.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List


def _parse_cors_origins(raw: str) -> List[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class ApiConfig:
    api_title: str = "AI Meeting Intelligence Platform API"
    api_version: str = "0.1.0"

    # 500 MB default cap on a single uploaded video. API-layer request
    # guard only -- not a VideoPipeline/settings.py concern.
    max_upload_size_bytes: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(500 * 1024 * 1024)))

    cors_allow_origins: List[str] = field(
        default_factory=lambda: _parse_cors_origins(os.getenv("CORS_ALLOW_ORIGINS", ""))
    )


@lru_cache
def get_api_config() -> ApiConfig:
    return ApiConfig()
