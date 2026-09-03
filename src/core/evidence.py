"""Channel-neutral evidence capability contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class EvidenceSource:
    """Provenance for an evidence object."""

    source_id: str
    source_type: str
    publisher: str | None = None
    uri: str | None = None
    retrieved_at: str | None = None
    verification_status: str = "UNVERIFIED"


@dataclass(frozen=True)
class EvidenceObject:
    """Metadata for user or externally sourced evidence.

    Binary content is intentionally represented by storage_ref and hash;
    storage implementation belongs to a provider adapter.
    """

    evidence_id: str
    evidence_type: str
    storage_ref: str
    sha256: str
    received_at: str
    captured_at: str | None = None
    source_description: str | None = None
    provenance: tuple[EvidenceSource, ...] = field(default_factory=tuple)
    access_policy_ref: str | None = None
    retention_policy_ref: str | None = None
    status: str = "ACTIVE"


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    relationship: str = "ATTACHMENT"


class EvidenceRepository(Protocol):
    """Provider-neutral evidence metadata contract."""

    def get(self, evidence_id: str) -> EvidenceObject | None:
        ...

    def save(self, evidence: EvidenceObject) -> None:
        ...


def validate_sha256(value: str) -> str:
    """Validate the canonical lowercase SHA-256 representation."""
    normalized = value.strip().lower()
    if len(normalized) != 64:
        raise ValueError("Evidence SHA-256 must contain 64 hexadecimal characters")
    try:
        int(normalized, 16)
    except ValueError as exc:
        raise ValueError("Evidence SHA-256 must be hexadecimal") from exc
    return normalized
