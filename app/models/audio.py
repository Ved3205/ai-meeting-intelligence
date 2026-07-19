"""
Audio Model
"""

from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class Audio:
    file_path: Path
    duration: float
    sample_rate: int
    channels: int
    codec: str