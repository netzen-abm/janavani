"""Provider-neutral in-memory evidence repository."""
from __future__ import annotations

from src.core.evidence import EvidenceObject, EvidenceRepository, validate_sha256


class InMemoryEvidenceRepository(EvidenceRepository):
    """Reference implementation for tests and local development."""

    def __init__(self) -> None:
        self._items: dict[str, EvidenceObject] = {}

    def get(self, evidence_id: str) -> EvidenceObject | None:
        return self._items.get(evidence_id)

    def save(self, evidence: EvidenceObject) -> None:
        normalized = validate_sha256(evidence.sha256)
        if normalized != evidence.sha256:
            evidence = EvidenceObject(
                evidence_id=evidence.evidence_id,
                evidence_type=evidence.evidence_type,
                storage_ref=evidence.storage_ref,
                sha256=normalized,
                received_at=evidence.received_at,
                captured_at=evidence.captured_at,
                source_description=evidence.source_description,
                provenance=evidence.provenance,
                access_policy_ref=evidence.access_policy_ref,
                retention_policy_ref=evidence.retention_policy_ref,
                status=evidence.status,
            )
        self._items[evidence.evidence_id] = evidence
