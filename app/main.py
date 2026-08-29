"""
app/main.py

FastAPI application entrypoint. No `app/main.py` existed in the
repository made available to me, so this is a NEW file.

Integrates with the REAL, pre-existing `app/config/settings.py` (its
`UPLOAD_DIR` is used directly -- no second upload directory is
invented). API-only concerns with no equivalent in settings.py
(title/version, CORS, upload size cap) live in `app/api/config.py`.

    Client
       |
       v
   FastAPI app
       |
       v
   Routers (health, meetings, query, summary, indexing)
       |
       v
   Existing pipelines (unmodified)

Run with:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.config import get_api_config
from app.api.routes import health, indexing, meetings, query, summary
from app.config.settings import UPLOAD_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

api_config = get_api_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the (real, settings.py-defined) upload directory exists
    # before the first request, rather than lazily creating it inside
    # a route on first use.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Startup: UPLOAD_DIR=%s", UPLOAD_DIR)
    yield


app = FastAPI(
    title=api_config.api_title,
    version=api_config.api_version,
    description="RAG-based Meeting Intelligence Platform API.",
    lifespan=lifespan,
)

# CORS is only configured if CORS_ALLOW_ORIGINS is set -- no wildcard
# default, and no unrequested infrastructure. Set e.g.
# CORS_ALLOW_ORIGINS="http://localhost:3000".
if api_config.cors_allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Defense-in-depth catch-all: routes already convert known failure
    modes to specific HTTPExceptions, but anything that still escapes
    is logged server-side (with traceback) and returns a generic 500
    to the client -- never a raw stack trace.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(health.router)
app.include_router(meetings.router)
app.include_router(query.router)
app.include_router(summary.router)
app.include_router(indexing.router)
