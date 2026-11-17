"""
API-layer-only configuration.

This module contains configuration that is specific to the HTTP/API layer
and does not belong in the application's main configuration.

The main application and pipeline/service settings are defined in:

    app/config/settings.py

Those settings include values such as:
    - UPLOAD_DIR
    - WHISPER_*
    - CHUNK_*
    - EMBEDDING_*
    - QDRANT_*
    - LLM_*
    - TOP_K
    - RETRIEVAL_LIMIT
    - SIMILARITY_THRESHOLD

Existing services and API routes can import those values directly from
`app.config.settings`.

This module only contains API-specific configuration:
    - API title and version for OpenAPI
    - CORS origins
    - HTTP upload size limit
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List


def _parse_cors_origins(raw: str) -> List[str]:
    """
    Parse comma-separated CORS origins from an environment variable.
    """
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class ApiConfig:
    """
    Configuration specific to the FastAPI HTTP layer.
    """

    api_title: str = "AI Meeting Intelligence Platform API"

    api_version: str = "0.1.0"

    # 500 MB default cap on a single uploaded video.
    #
    # This is an HTTP/API request guard and is intentionally separate
    # from the application/pipeline configuration in
    # app/config/settings.py.
    max_upload_size_bytes: int = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_BYTES",
            str(500 * 1024 * 1024),
        )
    )

    cors_allow_origins: List[str] = field(
        default_factory=lambda: _parse_cors_origins(
            os.getenv("CORS_ALLOW_ORIGINS", "")
        )
    )


@lru_cache
def get_api_config() -> ApiConfig:
    """
    Return the cached API configuration instance.
    """
    return ApiConfig()