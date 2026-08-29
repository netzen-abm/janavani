"""Reference in-memory implementations for platform contracts.

These implementations are deterministic test infrastructure. Production
persistence remains behind provider-specific adapters.
"""

from __future__ import annotations

from src.core.platform_contracts import ProvenanceRef, TrackingEvent


class InMemoryTrackingStore:
    def __init__(self) -> None:
        self._events: list[TrackingEvent] = []

    def append(self, event: TrackingEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self._events):
            return
        self._events.append(event)

    def list_for(self, subject_id: str) -> list[TrackingEvent]:
        return [event for event in self._events if event.subject_id == subject_id]


class InMemoryProvenanceStore:
    def __init__(self) -> None:
        self._records: dict[str, list[ProvenanceRef]] = {}

    def record(self, subject_id: str, provenance: ProvenanceRef) -> None:
        records = self._records.setdefault(subject_id, [])
        if provenance not in records:
            records.append(provenance)

    def list_for(self, subject_id: str) -> list[ProvenanceRef]:
        return list(self._records.get(subject_id, []))
