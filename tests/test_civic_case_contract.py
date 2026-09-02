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


def make_case() -> CivicCase:
    case = CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Delayed public service",
        narrative="The requested service has not been delivered.",
        created_by="user-1",
        related_office_id="office-1",
        consent_refs=["consent-1"],
    )
    case.start_review(event_id="event-1", occurred_at="2026-08-24T00:00:00Z")
    case.mark_ready(event_id="event-2", occurred_at="2026-08-24T00:01:00Z")
    return case


def test_review_and_consent_gate() -> None:
    case = CivicCase("case-1", CaseType.COMPLAINT, "Subject", "Narrative")
    case.start_review(event_id="event-1", occurred_at="2026-08-24T00:00:00Z")
    with pytest.raises(PermissionError):
        case.mark_ready(event_id="event-2", occurred_at="2026-08-24T00:01:00Z")


def test_submission_is_not_acknowledgement() -> None:
    case = make_case()
    case.begin_submission(event_id="event-3", occurred_at="2026-08-24T00:02:00Z")
    case.submit(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    assert case.status is CaseStatus.SUBMITTED
    assert not confirmed_delivery(case.status)


def test_acknowledgement_confirms_delivery() -> None:
    case = make_case()
    case.begin_submission(event_id="event-3", occurred_at="2026-08-24T00:02:00Z")
    case.submit(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    case.acknowledge(
        event_id="event-5",
        occurred_at="2026-08-24T00:04:00Z",
        source_channel="web",
        notes="Destination reference ACK-1",
    )
    assert case.status is CaseStatus.ACKNOWLEDGED
    assert confirmed_delivery(case.status)


def test_queue_preserves_submission_truth() -> None:
    case = make_case()
    case.begin_submission(event_id="event-3", occurred_at="2026-08-24T00:02:00Z")
    case.queue_submission(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    assert case.status is CaseStatus.QUEUED
    assert not confirmed_delivery(case.status)


def test_follow_up_and_resolution() -> None:
    case = make_case()
    case.begin_submission(event_id="event-3", occurred_at="2026-08-24T00:02:00Z")
    case.submit(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    case.acknowledge(event_id="event-5", occurred_at="2026-08-24T00:04:00Z")
    case.follow_up(event_id="event-6", occurred_at="2026-08-25T00:00:00Z")
    case.respond(event_id="event-7", occurred_at="2026-08-26T00:00:00Z")
    case.resolve(event_id="event-8", occurred_at="2026-08-27T00:00:00Z")
    case.close(event_id="event-9", occurred_at="2026-08-28T00:00:00Z")
    assert case.status is CaseStatus.CLOSED


def test_closed_case_rejects_evidence() -> None:
    case = make_case()
    case.begin_submission(event_id="event-3", occurred_at="2026-08-24T00:02:00Z")
    case.submit(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    case.acknowledge(event_id="event-5", occurred_at="2026-08-24T00:04:00Z")
    case.respond(event_id="event-6", occurred_at="2026-08-25T00:00:00Z")
    case.resolve(event_id="event-7", occurred_at="2026-08-26T00:00:00Z")
    case.close(event_id="event-8", occurred_at="2026-08-27T00:00:00Z")
    with pytest.raises(ValueError):
        case.add_evidence("evidence-1", event_id="event-9", occurred_at="2026-08-28T00:00:00Z")


def test_event_chain_rejects_submission_after_acknowledgement() -> None:
    events = [
        CaseEvent("1", "case-1", CaseEventType.ACKNOWLEDGED, "2026-08-24T00:00:00Z"),
        CaseEvent("2", "case-1", CaseEventType.SUBMITTED, "2026-08-24T00:01:00Z"),
    ]
    assert not validate_event_chain(events)
