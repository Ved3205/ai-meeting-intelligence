#!/usr/bin/env python
"""
scripts/test_indexing_pipeline.py

CLI for running the real IndexingPipeline against one video, several
videos, or a directory of videos.

Usage:
    python scripts/test_indexing_pipeline.py --video "C:\\path\\meeting.mp4"
    python scripts/test_indexing_pipeline.py --video video1.mp4 --video video2.mp4
    python scripts/test_indexing_pipeline.py --directory "C:\\path\\videos"
    python scripts/test_indexing_pipeline.py           # interactive prompt

Directory support is a disclosed convenience (see indexing_pipeline.py's
module docstring for why -- no documented PIPELINES.md confirmed this
requirement), not a guaranteed architecture feature.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pipelines.indexing_pipeline import IndexingPipeline  # noqa: E402

HR = "=" * 42


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the IndexingPipeline against one or more real videos."
    )
    parser.add_argument(
        "--video", action="append", default=[], metavar="PATH",
        help="A video file to index. Repeatable.",
    )
    parser.add_argument(
        "--directory", metavar="PATH",
        help="A directory whose contained videos will all be indexed (non-recursive).",
    )
    return parser.parse_args()


def _prompt_for_video() -> Path:
    print(HR)
    print(" AI MEETING INTELLIGENCE — INDEXING")
    print(HR)
    raw = input("\nEnter video path:\n> ").strip().strip('"')
    return Path(raw)


def _print_result(result) -> None:
    print()
    print(HR)
    print(" INDEXING COMPLETE")
    print(HR)
    for i, entry in enumerate(result.entries, start=1):
        print()
        print(f"[{i}/{len(result.entries)}] {entry.video_path}")
        if entry.status == "success":
            print(f"    Status:     SUCCESS")
            print(f"    Meeting ID: {entry.meeting_id}")
            print(f"    Chunks:     {entry.pipeline_result.total_chunks}")
            print(f"    Time:       {entry.elapsed_time:.2f}s")
        elif entry.status == "skipped_duplicate":
            print(f"    Status:     SKIPPED (duplicate path in this batch)")
        else:
            print(f"    Status:     FAILED")
            print(f"    Error:      {entry.error}")
            print(f"    Time:       {entry.elapsed_time:.2f}s")

    print()
    print(HR)
    print(f" Total videos:      {result.total_videos}")
    print(f" Successful videos: {result.successful_videos}")
    print(f" Failed videos:     {result.failed_videos}")
    print(f" Skipped videos:    {result.skipped_videos}")
    print(f" Total time:        {result.total_elapsed_time:.2f}s")
    print(HR)


def main() -> int:
    _configure_logging()
    args = _parse_args()

    inputs: list[str] = list(args.video)
    if args.directory:
        inputs.append(args.directory)

    if not inputs:
        inputs = [str(_prompt_for_video())]

    print()
    print("Input:")
    for item in inputs:
        print(f"  - {item}")

    pipeline = IndexingPipeline()
    try:
        result = pipeline.run(inputs)
    except ValueError as exc:
        print(f"\nInvalid input: {exc}")
        return 1

    _print_result(result)
    return 0 if result.failed_videos == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
