import pytest

from src.core.civic_case import (
    CaseEvent,
    CaseEventType,
    CaseStatus,
    CaseType,
    CivicCase,
    confirmed_delivery,
    validate_event_chain,
)


def ready_case() -> CivicCase:
    case = CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Delayed public service",
        narrative="The requested service has not been delivered.",
        created_by="user-1",
        related_office_id="office-1",
        consent_refs=["consent-1"],
    )
    case.mark_ready(event_id="event-1", occurred_at="2026-08-24T00:00:00Z", actor_id="user-1")
    return case


def test_case_requires_consent_before_ready() -> None:
    case = CivicCase(case_id="case-1", case_type=CaseType.COMPLAINT, subject="Subject", narrative="Narrative")
    with pytest.raises(PermissionError):
        case.mark_ready(event_id="event-1", occurred_at="2026-08-24T00:00:00Z")


def test_submission_does_not_mean_acknowledgement() -> None:
    case = ready_case()
    case.submit(event_id="event-2", occurred_at="2026-08-24T00:01:00Z", source_channel="web")
    assert case.status is CaseStatus.SUBMITTED
    assert confirmed_delivery(case.status) is False


def test_acknowledgement_confirms_delivery() -> None:
    case = ready_case()
    case.submit(event_id="event-2", occurred_at="2026-08-24T00:01:00Z")
    case.acknowledge(event_id="event-3", occurred_at="2026-08-24T00:02:00Z", source_channel="web", notes="Destination reference ACK-1")
    assert case.status is CaseStatus.ACKNOWLEDGED
    assert confirmed_delivery(case.status) is True


def test_closed_case_cannot_receive_new_evidence() -> None:
    case = ready_case()
    case.status = CaseStatus.RESPONDED
    case.close(event_id="event-2", occurred_at="2026-08-24T00:03:00Z")
    with pytest.raises(ValueError):
        case.add_evidence("evidence-1", event_id="event-3", occurred_at="2026-08-24T00:04:00Z")


def test_event_chain_rejects_submission_after_acknowledgement() -> None:
    events = [
        CaseEvent("1", "case-1", CaseEventType.ACKNOWLEDGED, "2026-08-24T00:00:00Z"),
        CaseEvent("2", "case-1", CaseEventType.SUBMITTED, "2026-08-24T00:01:00Z"),
    ]
    assert validate_event_chain(events) is False
