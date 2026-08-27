"""Provider-neutral persistence boundary for Evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.domain.evidence import Evidence, EvidenceKind, EvidenceStatus


class EvidenceRepository:
    """Minimal append-only local repository used until a canonical DB adapter is verified."""

    def __init__(self, path: str | Path = "database/evidence.jsonl") -> None:
        self.path = Path(path)

    def save(self, evidence: Evidence) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(self._to_record(evidence), ensure_ascii=False) + "\n")

    def get_by_id(self, evidence_id: str) -> Evidence | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("evidence_id") == evidence_id:
                    return self._from_record(record)
        return None

    def list_for_case(self, case_id: str) -> list[Evidence]:
        if not self.path.exists():
            return []
        results: list[Evidence] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("case_id") == case_id:
                    results.append(self._from_record(record))
        return results

    @staticmethod
    def _to_record(evidence: Evidence) -> dict[str, Any]:
        return {
            "evidence_id": evidence.evidence_id,
            "case_id": evidence.case_id,
            "kind": evidence.kind.value,
            "title": evidence.title,
            "source": evidence.source,
            "status": evidence.status.value,
            "content_ref": evidence.content_ref,
            "captured_at": evidence.captured_at.isoformat() if evidence.captured_at else None,
            "metadata": evidence.metadata,
            "provenance": evidence.provenance,
        }

    @staticmethod
    def _from_record(record: dict[str, Any]) -> Evidence:
        from datetime import datetime

        captured_at = record.get("captured_at")
        return Evidence(
            evidence_id=record["evidence_id"],
            case_id=record["case_id"],
            kind=EvidenceKind(record["kind"]),
            title=record["title"],
            source=record["source"],
            status=EvidenceStatus(record.get("status", EvidenceStatus.PROVIDED.value)),
            content_ref=record.get("content_ref"),
            captured_at=datetime.fromisoformat(captured_at) if captured_at else None,
            metadata=dict(record.get("metadata") or {}),
            provenance=list(record.get("provenance") or []),
        )


__all__ = ["EvidenceRepository"]
