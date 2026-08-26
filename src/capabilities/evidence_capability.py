"""Shared evidence and provenance capability boundary.

This module follows the locked ecosystem architecture: evidence capture is a
reusable capability, provenance is explicit, and interfaces/adapters do not
turn observations into verified findings. Concrete persistence, media capture,
and optional anchoring remain replaceable implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class EvidenceItem:
    """A user- or system-supplied evidence item with provenance metadata."""

    evidence_id: str
    evidence_type: str
    source: str
    captured_at: datetime
    content_hash: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be empty")
        if not self.evidence_type.strip():
            raise ValueError("evidence_type must not be empty")
        if self.captured_at.tzinfo is None:
            raise ValueError("captured_at must be timezone-aware")


@dataclass(frozen=True)
class EvidenceProvenance:
    """Source and transformation metadata; never a truth determination."""

    evidence_id: str
    source: str
    captured_at: datetime
    transformations: Sequence[str] = field(default_factory=tuple)
    integrity: Mapping[str, Any] = field(default_factory=dict)


class EvidenceStore(Protocol):
    """Provider-neutral persistence contract for evidence."""

    def save(self, item: EvidenceItem) -> None:
        ...

    def load(self, evidence_id: str) -> EvidenceItem | None:
        ...


class ProvenanceRecorder(Protocol):
    """Provider-neutral provenance recording contract."""

    def record(self, provenance: EvidenceProvenance) -> None:
        ...


class EvidenceCapability:
    """Reusable evidence capability exposed to independent interfaces."""

    name = "evidence"

    def __init__(
        self,
        store: EvidenceStore,
        provenance: ProvenanceRecorder,
    ) -> None:
        self._store = store
        self._provenance = provenance

    def capture(self, item: EvidenceItem) -> EvidenceItem:
        """Persist evidence and record its provenance without judging it."""
        self._store.save(item)
        self._provenance.record(
            EvidenceProvenance(
                evidence_id=item.evidence_id,
                source=item.source,
                captured_at=item.captured_at,
            )
        )
        return item

    def get(self, evidence_id: str) -> EvidenceItem | None:
        return self._store.load(evidence_id)


__all__ = [
    "EvidenceCapability",
    "EvidenceItem",
    "EvidenceProvenance",
    "EvidenceStore",
    "ProvenanceRecorder",
]
