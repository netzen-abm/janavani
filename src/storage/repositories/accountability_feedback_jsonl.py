"""Legacy-compatible JSONL adapter for canonical accountability feedback."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from src.core.accountability_feedback import AccountabilityFeedback


class JsonlAccountabilityFeedbackRepository:
    """Persist canonical feedback while retaining the existing JSONL data shape."""

    def __init__(self, path: str | Path = "database/ratings.jsonl"):
        self._path = Path(path)

    def save(self, feedback: AccountabilityFeedback) -> AccountabilityFeedback:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        actor_hash = _privacy_hash(feedback.actor_ref)
        entry = {
            "complaint_id": feedback.feedback_id,
            "timestamp": feedback.submitted_at,
            "office_id": feedback.office_id,
            "department_name": feedback.department_name,
            "rating": feedback.rating,
            "issue": feedback.issue,
            "user_hash": actor_hash,
            "status": "submitted",
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass
        return feedback

    def get(self, feedback_id: str) -> AccountabilityFeedback | None:
        for entry in self._read_entries():
            if str(entry.get("complaint_id")) == feedback_id:
                return _from_entry(entry)
        return None

    def list_for_office(self, office_id: str) -> list[AccountabilityFeedback]:
        return [
            _from_entry(entry)
            for entry in self._read_entries()
            if str(entry.get("office_id")) == office_id
        ]

    def _read_entries(self) -> list[dict[str, object]]:
        if not self._path.exists():
            return []
        records: list[dict[str, object]] = []
        with self._path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    records.append(value)
        return records


def _privacy_hash(actor_ref: str | None) -> str:
    value = actor_ref or "anonymous"
    return hashlib.sha256(str(value).encode()).hexdigest()[:10]


def _from_entry(entry: dict[str, object]) -> AccountabilityFeedback:
    return AccountabilityFeedback(
        feedback_id=str(entry.get("complaint_id", "")),
        office_id=str(entry.get("office_id", "")),
        rating=int(entry.get("rating", 0)),
        issue=str(entry.get("issue", "")),
        submitted_at=str(entry.get("timestamp", "")),
        department_name=str(entry.get("department_name")) if entry.get("department_name") else None,
        actor_ref=None,
        source_channel=None,
    )
