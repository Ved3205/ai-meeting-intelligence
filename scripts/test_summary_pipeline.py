#!/usr/bin/env python
"""
scripts/test_summary_pipeline.py

Interactive script: enter a meeting_id (obtained from a prior
video_pipeline.py run) and generate its Summary / Title / Keywords /
Action Items using the real SummaryPipeline. Does NOT re-index the
video.

Usage:
    python scripts/test_summary_pipeline.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pipelines.summary_pipeline import (  # noqa: E402
    MeetingNotFoundError,
    EmptyMeetingContentError,
    SummaryPipeline,
)

HR = "=" * 42
EXIT_COMMANDS = {"exit", "quit"}


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(result) -> None:
    print()
    print("Title:")
    print(result.title)
    print()
    print("Summary:")
    print(result.summary)
    print()
    print("Keywords:")
    for kw in result.keywords:
        print(f"  - {kw}")
    print()
    print("Action Items:")
    if result.action_items:
        for i, item in enumerate(result.action_items, start=1):
            print(f"  {i}. {item['description']}")
            print(f"     Owner: {item.get('owner') or '—'}")
            print(f"     Deadline: {item.get('deadline') or '—'}")
    else:
        print("  (none)")
    print()
    print(f"(based on {result.chunk_count} indexed chunks, {result.elapsed_time:.2f}s)")
    print()


def main() -> int:
    _configure_logging()

    print(HR)
    print(" AI MEETING INTELLIGENCE — SUMMARY")
    print(HR)
    print(" Enter a meeting_id from a prior video_pipeline.py run.")
    print(" Type 'exit' or 'quit' to stop.")
    print(HR)

    pipeline = SummaryPipeline()

    while True:
        print()
        try:
            meeting_id = input("Meeting ID:\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if not meeting_id:
            continue
        if meeting_id.lower() in EXIT_COMMANDS:
            print("Exiting.")
            return 0

        try:
            result = pipeline.run(meeting_id)
        except ValueError as exc:
            print(f"Invalid input: {exc}")
            continue
        except MeetingNotFoundError as exc:
            print(f"Meeting not found: {exc}")
            continue
        except EmptyMeetingContentError as exc:
            print(f"No usable content: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - deliberately broad for a REPL
            print(f"Summary generation failed: {exc}")
            continue

        _print_result(result)


if __name__ == "__main__":
    raise SystemExit(main())
