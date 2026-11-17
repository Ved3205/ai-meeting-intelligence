#!/usr/bin/env python
"""
scripts/test_video_pipeline.py

Small CLI utility to run the full VideoPipeline against a video file
and print nicely formatted progress and results.

Usage:
    python scripts/test_video_pipeline.py path/to/meeting.mp4
    python scripts/test_video_pipeline.py                       # uses DEFAULT_VIDEO_PATH below
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow running this script directly (`python scripts/test_video_pipeline.py`)
# without having installed the project as a package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pipelines.video_pipeline import VideoPipeline  # noqa: E402

# Change this if you want a zero-argument default target.
DEFAULT_VIDEO_PATH = Path(r"C:\Users\vedna\Downloads\Key Meeting - Engineering (Public Stream).mp4")

HR = "=" * 70


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_header(video_path: Path) -> None:
    print(HR)
    print(" AI MEETING INTELLIGENCE PLATFORM -- VIDEO PIPELINE TEST")
    print(HR)
    print(f" Video: {video_path}")
    print(HR)


def _print_result(result) -> None:
    print()
    print(HR)
    print(" PIPELINE RESULT")
    print(HR)
    status = "SUCCESS ✅" if result.success else "FAILED ❌"
    print(f" Status:              {status}")
    print(f" Meeting ID:          {result.meeting.meeting_id if result.meeting else '—'}")
    print(f" Meeting title:       {result.meeting.title if result.meeting else '—'}")

    if result.audio:
        print(f" Audio duration:      {result.audio.duration:.2f}s")
        print(f" Audio sample rate:   {result.audio.sample_rate} Hz")

    if result.transcript:
        print(f" Transcript language: {result.transcript.language}")
        print(f" Transcript segments: {len(result.transcript.segments)}")

    print(f" Chunks generated:    {result.total_chunks}")
    if result.chunks:
        embedded = sum(1 for c in result.chunks if c.embedding)
        print(f" Chunks embedded:     {embedded}")

    print(f" Elapsed time:        {result.elapsed_time:.2f}s")

    if result.warnings:
        print(f" Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"   - {w}")

    if result.errors:
        print(f" Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"   - {e}")

    print(HR)


def main() -> int:
    _configure_logging()

    if len(sys.argv) > 1:
        video_path = Path(sys.argv[1])
    else:
        video_path = DEFAULT_VIDEO_PATH
        print(f"No video path argument given, using default: {video_path}")

    if not video_path.exists():
        print(f"ERROR: video file does not exist: {video_path}")
        return 1

    _print_header(video_path)

    pipeline = VideoPipeline()
    result = pipeline.run(video_path)

    _print_result(result)

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
