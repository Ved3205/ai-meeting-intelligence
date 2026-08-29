"""
FFmpeg helper utilities.
"""

import shutil
import subprocess
from pathlib import Path

from app.utils.constants import (
    AUDIO_CODEC,
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS
)


def ffmpeg_exists() -> bool:
    """
    Check whether FFmpeg is installed.
    """
    return shutil.which("ffmpeg") is not None


def extract_audio(
    video_path: Path,
    output_audio_path: Path
) -> Path:
    """
    Extract audio from video using FFmpeg.
    """

    if not ffmpeg_exists():

        raise RuntimeError(
            "FFmpeg is not installed or not added to PATH."
        )

    output_audio_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [

        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-ac",
        str(AUDIO_CHANNELS),
        "-ar",
        str(AUDIO_SAMPLE_RATE),
        "-acodec",
        AUDIO_CODEC,
        str(output_audio_path)
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return output_audio_path


def get_video_duration(video_path: Path) -> float:
    """
    Return duration in seconds using ffprobe.
    """
    command = [
        "ffprobe",
        "-v",
        "error",

        "-show_entries",
        "format=duration",

        "-of",
        "default=noprint_wrappers=1:nokey=1",

        str(video_path)

    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return float(result.stdout.strip())