"""Provider-neutral evidence capability boundary.

Evidence is a first-class civic object. Storage, hashing, OCR, provenance,
and publication are implementation choices behind this boundary.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    evidence_id: str = Field(min_length=1, max_length=200)
    case_id: str = Field(min_length=1, max_length=200)
    filename: str = Field(min_length=1, max_length=500)
    media_type: str = Field(min_length=1, max_length=200)
    content_hash: str | None = None
    source: str = "citizen"
    metadata: dict[str, Any] = Field(default_factory=dict)
    captured_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceResult(BaseModel):
    ok: bool
    item: EvidenceItem | None = None
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    error_code: str | None = None


def fingerprint(content: bytes) -> str:
    """Return a deterministic SHA-256 fingerprint for evidence content."""
    return sha256(content).hexdigest()


class EvidenceCapability:
    """Small deterministic boundary; persistence and extraction stay external."""

    def register(self, item: EvidenceItem, content: bytes | None = None) -> EvidenceResult:
        if content is not None:
            item.content_hash = fingerprint(content)
        return EvidenceResult(
            ok=True,
            item=item,
            provenance=[{"type": "citizen_evidence", "evidence_id": item.evidence_id}],
        )
