"""
app/services/meeting_context_service.py

WHY THIS FILE EXISTS
---------------------
SummaryPipeline needs the complete indexed content for one meeting
(meeting_id) in order to generate a summary/title/keywords/action
items. Per SERVICES.md, no existing service documents a way to fetch
"all chunks for meeting_id X":

    - VectorStoreService.search(embedding, limit)  -- similarity search
      against a vector, no meeting_id filter, no "get all" method.
    - VectorStoreService.delete_meeting(meeting_id) -- write-only.
    - RetrievalService.retrieve(query: Query)       -- Query has no
      meeting_id field (per MODELS.md).

This is a genuine architecture gap, not an assumption to code around
silently. Per the task's explicit instruction ("create the minimum
necessary component rather than duplicating database logic inside the
pipeline"), this module adds the smallest possible helper -- and it
does so using ONLY RetrievalService's documented public API, never
touching Qdrant or embeddings directly.

HOW IT WORKS (and its limitation)
----------------------------------
`RetrievalService.retrieve()` is the only documented method that
returns `RetrievedChunk` objects (which do carry `meeting_id`). This
service issues one deliberately broad retrieval query (very low
`score_threshold`, large `top_k`) and filters the results down to the
requested `meeting_id` client-side, then reassembles them in
`chunk_index` order into a transcript-like string.

LIMITATION: this only finds chunks that rank within the top `max_chunks`
results of a generic query -- it is NOT a guaranteed complete listing
of every chunk for the meeting, especially in a large, multi-meeting
collection. The durable fix is a first-class
`VectorStoreService.get_chunks_by_meeting_id(meeting_id)` (or similar)
method, which was intentionally NOT added here since that would mean
modifying an existing, already-implemented service without being asked
to. If your real `VectorStoreService`/`RetrievalService` already expose
such a method, replace `MeetingContextService._fetch_chunks` with a
direct call to it -- that is the only place this workaround lives.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from app.models.query import Query
from app.models.retrieved_chunk import RetrievedChunk

from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

# Generic query text used purely to retrieve a broad sample of chunks
# to filter by meeting_id. This is NOT shown to the user and does not
# affect prompt content -- only `MeetingContext.transcript_text` (built
# from the chunks themselves) is ever passed to prompts.
_BROAD_QUERY_TEXT = "meeting discussion overview"
_DEFAULT_MAX_CHUNKS = 200


@dataclass
class MeetingContext:
    """Reconstructed context for one meeting, assembled from indexed chunks."""

    meeting_id: str
    chunks: List[RetrievedChunk] = field(default_factory=list)
    transcript_text: str = ""
    title: Optional[str] = None

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


class MeetingContextService:
    """
    Minimal helper that reconstructs a meeting's indexed content using
    only `RetrievalService`'s documented public API. See module
    docstring for why this exists and its known limitation.
    """

    def __init__(self, retrieval_service: Optional[RetrievalService] = None) -> None:
        self.retrieval_service = retrieval_service or RetrievalService()

    def get_context(
        self,
        meeting_id: str,
        max_chunks: int = _DEFAULT_MAX_CHUNKS,
    ) -> MeetingContext:
        """
        Reconstruct the indexed context for one meeting.

        Args:
            meeting_id: The meeting to reconstruct context for.
            max_chunks: Upper bound on chunks requested from retrieval
                (passed as `Query.top_k`).

        Returns:
            A `MeetingContext`. If no chunks belonging to `meeting_id`
            are found, `chunks` is empty and `transcript_text` is `""`
            -- callers are responsible for deciding whether that means
            "meeting not found" or "meeting has no content."
        """
        chunks = self._fetch_chunks(meeting_id, max_chunks)
        chunks.sort(key=lambda c: c.chunk_index)

        transcript_text = "\n\n".join(chunk.text for chunk in chunks if chunk.text)
        title = chunks[0].title if chunks and chunks[0].title else None

        return MeetingContext(
            meeting_id=meeting_id,
            chunks=chunks,
            transcript_text=transcript_text,
            title=title,
        )

    def _fetch_chunks(self, meeting_id: str, max_chunks: int) -> List[RetrievedChunk]:
        """Retrieve a broad chunk sample and filter to this meeting_id."""
        query = Query(question=_BROAD_QUERY_TEXT, top_k=max_chunks, score_threshold=0.0)
        results = self.retrieval_service.retrieve(query)
        return [result.chunk for result in results if result.chunk.meeting_id == meeting_id]
