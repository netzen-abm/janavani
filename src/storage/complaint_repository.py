"""Provider-neutral complaint persistence boundary.

The repository owns persistence mechanics; services own business behavior.
The initial implementation deliberately preserves the existing JSONL storage
until the canonical Supabase/PostgreSQL runtime path is verified.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class ComplaintRepository:
    """Minimal repository contract backed by the existing local JSONL store."""

    def __init__(self, path: str | Path = "database/complaints.jsonl") -> None:
        self.path = Path(path)

    def save(self, record: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(record)
        payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def get_by_id(self, complaint_id: str) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("complaint_id") == complaint_id:
                    return record
        return None


__all__ = ["ComplaintRepository"]
