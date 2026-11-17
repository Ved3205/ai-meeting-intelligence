"""
app/api/dependencies.py

Provides cached, process-lifetime pipeline instances for use as
FastAPI dependencies (`Depends(...)`). No new DI framework is
introduced -- this is stdlib `functools.lru_cache` plus FastAPI's
existing `Depends` mechanism.

WHY THIS MATTERS: `VideoPipeline()` eagerly constructs
`TranscriptionService()`, `EmbeddingService()`, etc. in its
`__init__` (per the real, unmodified `video_pipeline.py`), which load
expensive models (Whisper, the embedding model). Constructing a new
`VideoPipeline()` per request would reload those models on every
call. `lru_cache` ensures each pipeline is constructed exactly once
per process and reused across requests.

`IndexingPipeline` is given the SAME cached `VideoPipeline` instance
(rather than constructing its own), so the `/meetings/upload` and
`/indexing` routes never end up with two separate copies of the
expensive underlying services.
"""

from __future__ import annotations

from functools import lru_cache

from app.pipelines.indexing_pipeline import IndexingPipeline
from app.pipelines.query_pipeline import QueryPipeline
from app.pipelines.summary_pipeline import SummaryPipeline
from app.pipelines.video_pipeline import VideoPipeline


@lru_cache
def get_video_pipeline() -> VideoPipeline:
    return VideoPipeline()


@lru_cache
def get_query_pipeline() -> QueryPipeline:
    return QueryPipeline()


@lru_cache
def get_summary_pipeline() -> SummaryPipeline:
    return SummaryPipeline()


@lru_cache
def get_indexing_pipeline() -> IndexingPipeline:
    # Reuses the same cached VideoPipeline instance -- see module docstring.
    return IndexingPipeline(video_pipeline=get_video_pipeline())
