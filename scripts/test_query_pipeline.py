#!/usr/bin/env python
"""
scripts/test_query_pipeline.py

Interactive RAG query tool against already-indexed meeting data.
Does NOT re-index anything -- it only queries whatever is currently in
Qdrant via the real QueryPipeline (real RetrievalService + LLMService).

Usage:
    python scripts/test_query_pipeline.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pipelines.query_pipeline import QueryPipeline  # noqa: E402

HR = "=" * 42
EXIT_COMMANDS = {"exit", "quit"}


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _format_timestamp(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _print_response(response) -> None:
    print()
    print(f"Retrieved chunks: {len(response.retrieved_chunks)}")
    if response.retrieved_chunks:
        print()
        print("Sources:")
        for i, chunk in enumerate(response.retrieved_chunks, start=1):
            print(
                f"  [{i}] {_format_timestamp(chunk.start_time)} - "
                f"{_format_timestamp(chunk.end_time)}"
            )
    print()
    print("Answer:")
    print(response.answer)
    print()
    print("Confidence:")
    print(f"{response.confidence:.2f}")
    print()


def main() -> int:
    _configure_logging()

    print(HR)
    print(" AI MEETING INTELLIGENCE — RAG QUERY")
    print(HR)
    print(" Type 'exit' or 'quit' to stop.")
    print(HR)

    pipeline = QueryPipeline()

    while True:
        print()
        try:
            question = input("Enter question:\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("Exiting.")
            return 0

        try:
            response = pipeline.run(question)
        except ValueError as exc:
            print(f"Invalid input: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - deliberately broad for a REPL
            print(f"Query failed: {exc}")
            continue

        _print_response(response)


if __name__ == "__main__":
    raise SystemExit(main())
