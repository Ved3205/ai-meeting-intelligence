"""
JSON helper utilities.
"""

import json
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict:
    """
    Load JSON file.
    """
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path: Path, data: Any) -> None:
    """
    Save dictionary as JSON.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def append_json(file_path: Path, data: dict) -> None:
    """
    Append data into JSON list.
    """

    if file_path.exists():

        existing = load_json(file_path)

    else:

        existing = []

    existing.append(data)

    save_json(file_path, existing)


def pretty_print_json(data: dict) -> str:
    """
    Return formatted JSON string.
    """

    return json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    )