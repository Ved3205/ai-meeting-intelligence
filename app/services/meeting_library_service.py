"""
services/meeting_library_service.py

Reads meetings back out of Qdrant (list, detail, transcript, delete).
"""

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, FilterSelector, MatchValue

from app.config.settings import COLLECTION_NAME
from app.models.meeting_info import MeetingInfo
from app.vectorstore.shared_client import get_qdrant_client

_PAGE_SIZE = 256


def _meeting_filter(meeting_id: str) -> Filter:
    return Filter(must=[FieldCondition(key="meeting_id", match=MatchValue(value=meeting_id))])


class MeetingLibraryService:

    def __init__(self, client: QdrantClient | None = None):
        self.client = client or get_qdrant_client()

    def _scroll(self, query_filter: Filter | None = None):
        # Collection is only created on first upload.
        if not self.client.collection_exists(COLLECTION_NAME):
            return
        offset = None
        while True:
            points, offset = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=query_filter,
                limit=_PAGE_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            yield from points
            if offset is None:
                break

    @staticmethod
    def _group(points) -> list[MeetingInfo]:
        meetings: dict[str, MeetingInfo] = {}
        for point in points:
            p = point.payload
            info = meetings.get(p["meeting_id"])
            if info is None:
                info = MeetingInfo(
                    meeting_id=p["meeting_id"],
                    title=p.get("title"),
                    filename=p.get("filename"),
                    language=p.get("language"),
                    total_chunks=0,
                    duration=0.0,
                    uploaded_at=p.get("uploaded_at"),
                )
                meetings[info.meeting_id] = info
            info.total_chunks += 1
            info.duration = max(info.duration, p.get("end_time", 0.0))
        return list(meetings.values())

    def list_meetings(self) -> list[MeetingInfo]:
        meetings = self._group(self._scroll())
        # Newest first, meetings without a timestamp go last.
        meetings.sort(key=lambda m: m.uploaded_at or "", reverse=True)
        return meetings

    def get_meeting(self, meeting_id: str) -> MeetingInfo | None:
        found = self._group(self._scroll(_meeting_filter(meeting_id)))
        return found[0] if found else None

    def get_chunks(self, meeting_id: str) -> list[dict]:
        payloads = [p.payload for p in self._scroll(_meeting_filter(meeting_id))]
        return sorted(payloads, key=lambda p: p["chunk_index"])

    def delete_meeting(self, meeting_id: str) -> None:
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=FilterSelector(filter=_meeting_filter(meeting_id)),
        )
