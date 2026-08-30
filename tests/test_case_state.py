import pytest

from src.core.capabilities.case_state import SharedCaseStateRepository
from src.core.contracts.case_state import CaseEvent, CaseLifecycle, PersistentCaseState


def test_case_reference_and_events_persist():
    repo = SharedCaseStateRepository()
    case = repo.create("JV-20260830-ABC123")
    event = repo.add_event(case.reference.case_id, "document_delivered", "Initial complaint document delivered to citizen")
    loaded = repo.get(case.reference.case_id)
    assert loaded.reference.reference_number == "JV-20260830-ABC123"
    assert loaded.events[0].event_id == event.event_id


def test_raw_sensitive_data_cannot_be_stored_remotely():
    repo = SharedCaseStateRepository()
    case = repo.create("JV-20260830-ABC123")
    event = CaseEvent("evt-1", case.reference.case_id, "evidence", PersistentCaseState.now(), "Private evidence", sensitive_data_stored_remotely=True)
    with pytest.raises(ValueError):
        case.add_event(event)


def test_lifecycle_can_move_to_waiting_for_trigger():
    repo = SharedCaseStateRepository()
    case = repo.create("JV-20260830-ABC123")
    updated = repo.set_lifecycle(case.reference.case_id, CaseLifecycle.WAITING_FOR_TRIGGER)
    assert updated.reference.lifecycle == CaseLifecycle.WAITING_FOR_TRIGGER
