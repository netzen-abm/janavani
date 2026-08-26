"""Contract tests for the shared evidence/provenance capability."""

from datetime import datetime, timezone

import pytest

from src.capabilities.evidence_capability import (
    EvidenceCapability,
    EvidenceItem,
    EvidenceProvenance,
)


class InMemoryEvidenceStore:
    def __init__(self):
        self.items = {}

    def save(self, item):
        self.items[item.evidence_id] = item

    def load(self, evidence_id):
        return self.items.get(evidence_id)


class InMemoryProvenanceRecorder:
    def __init__(self):
        self.records = []

    def record(self, provenance):
        self.records.append(provenance)


def test_capture_persists_evidence_and_provenance_without_verifying_claim():
    store = InMemoryEvidenceStore()
    recorder = InMemoryProvenanceRecorder()
    capability = EvidenceCapability(store, recorder)
    captured_at = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    item = EvidenceItem(
        evidence_id="ev-001",
        evidence_type="document",
        source="user",
        captured_at=captured_at,
        content_hash="sha256:example",
    )

    result = capability.capture(item)

    assert result == item
    assert store.load("ev-001") == item
    assert len(recorder.records) == 1
    assert isinstance(recorder.records[0], EvidenceProvenance)
    assert recorder.records[0].source == "user"
    assert recorder.records[0].captured_at == captured_at


def test_capture_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        EvidenceItem(
            evidence_id="ev-002",
            evidence_type="image",
            source="user",
            captured_at=datetime(2026, 8, 26, 10, 0),
        )


def test_get_returns_none_for_unknown_evidence():
    capability = EvidenceCapability(InMemoryEvidenceStore(), InMemoryProvenanceRecorder())

    assert capability.get("missing") is None
