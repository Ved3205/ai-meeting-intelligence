"""
app/api/routes/health.py

Simple liveness endpoint. No infrastructure health checks (Qdrant,
Ollama, etc.) are performed here -- those are exercised by the
pipelines' own real-integration tests, not API-level health checks.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check", description="Returns a simple liveness indicator.")
def health_check() -> dict:
    return {"status": "ok"}
