"""Backward-compatible JSONL persistence adapter for civic cases.

The canonical storage contract is ``CaseRepository``. This adapter retains
legacy JSONL storage while the Supabase/PostgreSQL runtime is being verified.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class ComplaintRepository:
    """Legacy-compatible repository implementing the CaseRepository contract."""

    def __init__(self, path: str | Path = "database/complaints.jsonl") -> None:
        self.path = Path(path)

    def save(self, record: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(record)
        payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        # During migration, support both canonical case_id and legacy
        # complaint_id records without rewriting existing data.
        if "case_id" not in payload and "complaint_id" in payload:
            payload["case_id"] = payload["complaint_id"]
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def get_by_id(self, case_id: str) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("case_id") == case_id or record.get("complaint_id") == case_id:
                    return record
        return None


__all__ = ["ComplaintRepository"]
