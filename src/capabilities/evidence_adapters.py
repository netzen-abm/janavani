"""Reference evidence adapters for the shared capability boundary.

These adapters deliberately remain infrastructure-neutral. They make the
existing evidence capability usable in tests and lightweight deployments
without creating a second persistence model. Production adapters can implement
the same protocols around the canonical storage ownership described in
``docs/STORAGE_OWNERSHIP_MAP_2026-08-23.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .evidence_capability import EvidenceItem, EvidenceProvenance


@dataclass
class InMemoryEvidenceStore:
    """Reference store for tests and local capability composition only."""

    items: dict[str, EvidenceItem] = field(default_factory=dict)

    def save(self, item: EvidenceItem) -> None:
        self.items[item.evidence_id] = item

    def load(self, evidence_id: str) -> EvidenceItem | None:
        return self.items.get(evidence_id)


@dataclass
class InMemoryProvenanceRecorder:
    """Reference provenance recorder for tests and local composition."""

    records: list[EvidenceProvenance] = field(default_factory=list)

    def record(self, provenance: EvidenceProvenance) -> None:
        self.records.append(provenance)


class MetadataEvidenceStore:
    """Small adapter over a caller-owned mapping.

    This is intentionally not a database adapter. It provides a deterministic
    bridge for composition tests while the canonical durable repository layer
    is being verified.
    """

    def __init__(self, backing: dict[str, EvidenceItem] | None = None) -> None:
        self._backing = backing if backing is not None else {}

    def save(self, item: EvidenceItem) -> None:
        self._backing[item.evidence_id] = item

    def load(self, evidence_id: str) -> EvidenceItem | None:
        return self._backing.get(evidence_id)


__all__ = [
    "InMemoryEvidenceStore",
    "InMemoryProvenanceRecorder",
    "MetadataEvidenceStore",
]
