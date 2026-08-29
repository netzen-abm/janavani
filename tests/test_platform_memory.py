from src.core.platform_contracts import ProvenanceRef, TrackingEvent
from src.core.platform_memory import InMemoryProvenanceStore, InMemoryTrackingStore


def test_tracking_store_is_idempotent_and_scoped():
    store = InMemoryTrackingStore()
    event = TrackingEvent(event_id="e1", subject_id="case-1", event_type="submitted")
    store.append(event)
    store.append(event)
    store.append(TrackingEvent(event_id="e2", subject_id="case-2", event_type="submitted"))

    assert store.list_for("case-1") == [event]
    assert store.list_for("case-2")[0].event_id == "e2"


def test_provenance_store_deduplicates_records():
    store = InMemoryProvenanceStore()
    ref = ProvenanceRef(source_id="gov-1")
    store.record("case-1", ref)
    store.record("case-1", ref)

    assert store.list_for("case-1") == [ref]
    assert store.list_for("missing") == []
