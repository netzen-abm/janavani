"""Shared JSONL operations for legacy local persistence.

Atomic replacement prevents a partially written file on ordinary process
failure. It does not provide cross-process locking or transaction isolation.
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


def read_jsonl_records(path: str | os.PathLike[str]) -> list[dict[str, Any]]:
    """Read JSON objects from non-empty lines; malformed JSON remains an error."""
    with open(path, "r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl_records(
    path: str | os.PathLike[str],
    records: Iterable[dict[str, Any]],
) -> None:
    """Serialize records and atomically replace the destination file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = stream.name
            for record in records:
                stream.write(json.dumps(record) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
