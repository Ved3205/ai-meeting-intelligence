"""
services/summary_cache_service.py

Keeps generated summaries as JSON files so the LLM is not called twice.
"""

import json
import re
from pathlib import Path

from app.config.settings import DATA_DIR

SUMMARY_DIR = DATA_DIR / "summaries"

_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class SummaryCacheService:

    def __init__(self, directory: Path = SUMMARY_DIR):
        self.directory = directory

    def _path(self, meeting_id: str) -> Path | None:
        # meeting_id comes from the URL, so never build a path from anything odd.
        if not _SAFE_ID.match(meeting_id):
            return None
        return self.directory / f"{meeting_id}.json"

    def get(self, meeting_id: str) -> dict | None:
        path = self._path(meeting_id)
        if path is None or not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def save(self, meeting_id: str, summary: dict) -> None:
        path = self._path(meeting_id)
        if path is None:
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary), encoding="utf-8")

    def delete(self, meeting_id: str) -> None:
        path = self._path(meeting_id)
        if path is not None and path.exists():
            path.unlink()
