"""Explicit, read-only recovery boundary for preserved legacy JSONL data.

This module deliberately does not know about production providers. It reads a
preserved JSONL source, validates each record as JSON, and produces an
inspectable report. Transformation into canonical domain records is owned by
source-specific migration code, not by a generic storage adapter.

No source file is modified or deleted by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True)
class LegacyJsonlRecord:
    """One source line and its parsed JSON value."""

    line_number: int
    value: dict[str, Any]


@dataclass(frozen=True)
class LegacyJsonlIssue:
    """A source validation issue that requires review before migration."""

    line_number: int
    reason: str


@dataclass(frozen=True)
class LegacyJsonlReport:
    """Deterministic validation result for one preserved source."""

    source: str
    records: tuple[LegacyJsonlRecord, ...]
    issues: tuple[LegacyJsonlIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


class LegacyJsonlSource:
    """Read-only adapter for a preserved JSONL migration/recovery source."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    def iter_records(self) -> Iterator[LegacyJsonlRecord]:
        """Yield valid object records without changing the source."""
        with self._path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                text = raw_line.strip()
                if not text:
                    continue
                value = json.loads(text)
                if not isinstance(value, dict):
                    raise ValueError(
                        f"JSONL line {line_number} must contain a JSON object"
                    )
                yield LegacyJsonlRecord(line_number=line_number, value=value)

    def validate(self) -> LegacyJsonlReport:
        """Validate the complete source without mutating it."""
        records: list[LegacyJsonlRecord] = []
        issues: list[LegacyJsonlIssue] = []

        if not self._path.exists():
            return LegacyJsonlReport(
                source=str(self._path),
                records=(),
                issues=(LegacyJsonlIssue(0, "source file does not exist"),),
            )

        with self._path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                text = raw_line.strip()
                if not text:
                    continue
                try:
                    value = json.loads(text)
                except json.JSONDecodeError as exc:
                    issues.append(
                        LegacyJsonlIssue(line_number, f"invalid JSON: {exc.msg}")
                    )
                    continue
                if not isinstance(value, dict):
                    issues.append(
                        LegacyJsonlIssue(
                            line_number, "record must be a JSON object"
                        )
                    )
                    continue
                records.append(LegacyJsonlRecord(line_number, value))

        return LegacyJsonlReport(
            source=str(self._path),
            records=tuple(records),
            issues=tuple(issues),
        )
