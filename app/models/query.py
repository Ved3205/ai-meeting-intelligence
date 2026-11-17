"""
models/query.py
"""
from dataclasses import dataclass

@dataclass(slots=True)
class Query:
    question: str
    top_k: int = 5
    score_threshold: float = 0.70
    meeting_id: str | None = None