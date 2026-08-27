"""Canonical Evidence domain object for Janavani cases.

Evidence is a durable, source-aware reference attached to a Case. Content storage,
transport, and provider implementations remain outside this domain object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class EvidenceKind(str, Enum):
    DOCUMENT = "document"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    WEB = "web"
    TESTIMONY = "testimony"
    RECORD = "record"
    OTHER = "other"


class EvidenceStatus(str, Enum):
    PROVIDED = "provided"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Evidence:
    """Canonical evidence metadata; payload lives behind ``content_ref``."""

    evidence_id: str
    case_id: str
    kind: EvidenceKind
    title: str
    source: str
    status: EvidenceStatus = EvidenceStatus.PROVIDED
    content_ref: str | None = None
    captured_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        case_id: str,
        kind: EvidenceKind,
        title: str,
        source: str,
        *,
        content_ref: str | None = None,
        captured_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        provenance: list[str] | None = None,
        status: EvidenceStatus = EvidenceStatus.PROVIDED,
    ) -> "Evidence":
        case_id = case_id.strip()
        title = title.strip()
        source = source.strip()
        if not case_id:
            raise ValueError("case_id is required")
        if not title:
            raise ValueError("evidence title is required")
        if not source:
            raise ValueError("evidence source is required")
        return cls(
            evidence_id=f"EVD-{uuid4().hex[:12].upper()}",
            case_id=case_id,
            kind=kind,
            title=title,
            source=source,
            status=status,
            content_ref=content_ref.strip() if content_ref and content_ref.strip() else None,
            captured_at=captured_at,
            metadata=dict(metadata or {}),
            provenance=[item.strip() for item in (provenance or []) if item.strip()],
        )

    def verify(self) -> "Evidence":
        """Return a verified copy; provenance is required for verification."""
        if not self.provenance:
            raise ValueError("cannot verify evidence without provenance")
        return Evidence(
            evidence_id=self.evidence_id,
            case_id=self.case_id,
            kind=self.kind,
            title=self.title,
            source=self.source,
            status=EvidenceStatus.VERIFIED,
            content_ref=self.content_ref,
            captured_at=self.captured_at,
            metadata=dict(self.metadata),
            provenance=list(self.provenance),
        )


__all__ = ["Evidence", "EvidenceKind", "EvidenceStatus"]
