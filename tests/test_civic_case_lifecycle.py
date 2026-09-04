import pytest

from src.core.case_lifecycle import CASE_STATUS_TRANSITIONS, can_transition, require_transition
from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase, validate_event_chain


def _case(*, consent=True) -> CivicCase:
    return CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Road damage",
        narrative="Road is damaged",
        consent_refs=["consent-1"] if consent else [],
    )


def test_canonical_transition_contract_has_all_statuses():
    assert set(CASE_STATUS_TRANSITIONS) == set(CaseStatus)


def test_transition_helpers_fail_closed():
    assert can_transition(CaseStatus.DRAFT, CaseStatus.REVIEW)
    assert can_transition(CaseStatus.SUBMITTED, CaseStatus.ACKNOWLEDGED)
    assert not can_transition(CaseStatus.DRAFT, CaseStatus.SUBMITTED)
    assert not can_transition(CaseStatus.CLOSED, CaseStatus.REVIEW)
    require_transition(CaseStatus.READY, CaseStatus.SUBMITTING)
    with pytest.raises(ValueError):
        require_transition(CaseStatus.READY, CaseStatus.ACKNOWLEDGED)


def test_transition_matrix_happy_path():
    case = _case()
    case.start_review(event_id="e1", occurred_at="2026-01-01T00:00:00Z")
    case.mark_ready(event_id="e2", occurred_at="2026-01-01T00:01:00Z")
    case.begin_submission(event_id="e3", occurred_at="2026-01-01T00:02:00Z")
    case.queue_submission(event_id="e4", occurred_at="2026-01-01T00:03:00Z")
    case.submit(event_id="e5", occurred_at="2026-01-01T00:04:00Z")
    case.acknowledge(event_id="e6", occurred_at="2026-01-01T00:05:00Z")
    case.follow_up(event_id="e7", occurred_at="2026-01-01T00:06:00Z")
    case.respond(event_id="e8", occurred_at="2026-01-01T00:07:00Z")
    case.resolve(event_id="e9", occurred_at="2026-01-01T00:08:00Z")
    case.close(event_id="e10", occurred_at="2026-01-01T00:09:00Z")
    assert case.status is CaseStatus.CLOSED
    assert validate_event_chain(case.events)


def test_ready_requires_explicit_consent():
    case = _case(consent=False)
    case.start_review(event_id="e1", occurred_at="2026-01-01T00:00:00Z")
    with pytest.raises(PermissionError):
        case.mark_ready(event_id="e2", occurred_at="2026-01-01T00:01:00Z")


def test_invalid_transitions_fail_closed():
    case = _case()
    with pytest.raises(ValueError):
        case.begin_submission(event_id="e1", occurred_at="now")
    with pytest.raises(ValueError):
        case.submit(event_id="e2", occurred_at="now")
    with pytest.raises(ValueError):
        case.acknowledge(event_id="e3", occurred_at="now")
    with pytest.raises(ValueError):
        case.resolve(event_id="e4", occurred_at="now")
    with pytest.raises(ValueError):
        case.close(event_id="e5", occurred_at="now")


def test_event_chain_rejects_events_after_closed():
    events = [
        CaseEvent("e1", "case-1", CaseEventType.CREATED, "now"),
        CaseEvent("e2", "case-1", CaseEventType.CLOSED, "now"),
        CaseEvent("e3", "case-1", CaseEventType.EDITED, "now"),
    ]
    assert not validate_event_chain(events)
