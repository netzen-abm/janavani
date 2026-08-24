"""Channel-neutral evidence contract for civic cases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceRelationship(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    ATTACHMENT = "attachment"
    SOURCE = "source"
    OTHER = "other"


class EvidenceStatus(str, Enum):
    ACTIVE = "active"
    DISPUTED = "disputed"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass(frozen=True)
class EvidenceObject:
    evidence_id: str
    storage_ref: str
    sha256: str
    evidence_type: str
    owner_id: str | None = None
    source_description: str | None = None
    access_policy_ref: str | None = None
    retention_policy_ref: str | None = None
    status: EvidenceStatus = EvidenceStatus.ACTIVE


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    relationship: EvidenceRelationship


def validate_evidence(evidence: EvidenceObject) -> None:
    """Enforce minimum integrity metadata without deciding evidence truth."""
    if not evidence.evidence_id or not evidence.storage_ref:
        raise ValueError("evidence_id and storage_ref are required")
    if len(evidence.sha256) != 64:
        raise ValueError("sha256 must be a 64-character hexadecimal digest")
    try:
        int(evidence.sha256, 16)
    except ValueError as exc:
        raise ValueError("sha256 must be hexadecimal") from exc
    if evidence.status is EvidenceStatus.ACTIVE and not evidence.access_policy_ref:
        raise ValueError("active evidence requires an access policy reference")
