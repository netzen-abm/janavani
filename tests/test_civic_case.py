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


def draft_case() -> CivicCase:
    return CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Delayed public service",
        narrative="The requested service has not been delivered.",
        created_by="user-1",
        related_office_id="office-1",
    )


def ready_case() -> CivicCase:
    case = draft_case()
    case.consent_refs.append("consent-1")
    case.mark_ready(event_id="event-1", occurred_at="2026-08-24T00:00:00Z", actor_id="user-1")
    return case


def submitted_case() -> CivicCase:
    case = ready_case()
    case.submit(event_id="event-2", occurred_at="2026-08-24T00:01:00Z", source_channel="web")
    return case


def acknowledged_case() -> CivicCase:
    case = submitted_case()
    case.acknowledge(event_id="event-3", occurred_at="2026-08-24T00:02:00Z", source_channel="web")
    return case


def test_case_requires_consent_before_ready() -> None:
    with pytest.raises(PermissionError):
        draft_case().mark_ready(event_id="event-1", occurred_at="2026-08-24T00:00:00Z")


def test_submission_does_not_mean_acknowledgement() -> None:
    case = submitted_case()
    assert case.status is CaseStatus.SUBMITTED
    assert confirmed_delivery(case.status) is False


def test_acknowledgement_confirms_delivery() -> None:
    case = acknowledged_case()
    assert case.status is CaseStatus.ACKNOWLEDGED
    assert confirmed_delivery(case.status) is True


def test_complete_response_close_archive_lifecycle() -> None:
    case = acknowledged_case()
    case.start_processing(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    case.respond(event_id="event-5", occurred_at="2026-08-24T00:04:00Z", notes="Response issued")
    case.close(event_id="event-6", occurred_at="2026-08-24T00:05:00Z")
    case.archive(event_id="event-7", occurred_at="2026-08-24T00:06:00Z")
    assert case.status is CaseStatus.ARCHIVED


def test_escalation_can_close_case() -> None:
    case = acknowledged_case()
    case.start_processing(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    case.escalate(event_id="event-5", occurred_at="2026-08-24T00:04:00Z", notes="No response")
    case.close(event_id="event-6", occurred_at="2026-08-24T00:05:00Z")
    assert case.status is CaseStatus.CLOSED


def test_invalid_transitions_are_rejected() -> None:
    case = draft_case()
    with pytest.raises(ValueError):
        case.submit(event_id="event-1", occurred_at="2026-08-24T00:00:00Z")
    with pytest.raises(ValueError):
        case.acknowledge(event_id="event-2", occurred_at="2026-08-24T00:01:00Z")


def test_terminal_cases_cannot_be_modified() -> None:
    case = acknowledged_case()
    case.start_processing(event_id="event-4", occurred_at="2026-08-24T00:03:00Z")
    case.respond(event_id="event-5", occurred_at="2026-08-24T00:04:00Z")
    case.close(event_id="event-6", occurred_at="2026-08-24T00:05:00Z")
    with pytest.raises(ValueError):
        case.add_evidence("evidence-1", event_id="event-7", occurred_at="2026-08-24T00:06:00Z")
    case.archive(event_id="event-8", occurred_at="2026-08-24T00:07:00Z")
    with pytest.raises(ValueError):
        case.close(event_id="event-9", occurred_at="2026-08-24T00:08:00Z")


def test_duplicate_event_id_is_rejected() -> None:
    case = ready_case()
    case.submit(event_id="event-2", occurred_at="2026-08-24T00:01:00Z")
    with pytest.raises(ValueError):
        case.acknowledge(event_id="event-2", occurred_at="2026-08-24T00:02:00Z")


def test_event_chain_rejects_duplicate_ids() -> None:
    events = [
        CaseEvent("1", "case-1", CaseEventType.SUBMITTED, "2026-08-24T00:00:00Z"),
        CaseEvent("1", "case-1", CaseEventType.ACKNOWLEDGED, "2026-08-24T00:01:00Z"),
    ]
    assert validate_event_chain(events) is False
