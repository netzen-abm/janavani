from src.capabilities.escalation import (
    EscalationAction,
    EscalationCapability,
    EscalationContext,
    EscalationStatus,
)
from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CivicCase, CaseType


def _case(status=CaseStatus.ACKNOWLEDGED, events=()):
    return CivicCase(
        case_id="case-test",
        case_type=CaseType.COMPLAINT,
        subject="Test matter",
        narrative="Test narrative",
        created_by="citizen:test",
        status=status,
        events=list(events),
    )


def test_follow_up_precedes_escalation():
    result = EscalationCapability().recommend(EscalationContext(case=_case()))
    assert result.action is EscalationAction.FOLLOW_UP
    assert result.status is EscalationStatus.NOT_DUE


def test_recorded_follow_up_recommends_administrative_escalation():
    event = CaseEvent(
        event_id="event-follow-up",
        case_id="case-test",
        event_type=CaseEventType.FOLLOW_UP,
        occurred_at="2026-09-09T00:00:00+00:00",
    )
    result = EscalationCapability().recommend(
        EscalationContext(case=_case(status=CaseStatus.FOLLOW_UP, events=(event,)))
    )
    assert result.action is EscalationAction.ADMINISTRATIVE_HEAD
    assert result.status is EscalationStatus.USER_ACTION_REQUIRED


def test_unsatisfactory_report_recommends_escalation():
    result = EscalationCapability().recommend(
        EscalationContext(case=_case(), user_report="unsatisfactory")
    )
    assert result.action is EscalationAction.ADMINISTRATIVE_HEAD
    assert result.status is EscalationStatus.RECOMMENDED


def test_existing_escalation_is_not_repeated():
    event = CaseEvent(
        event_id="event-escalated",
        case_id="case-test",
        event_type=CaseEventType.ESCALATED,
        occurred_at="2026-09-09T00:00:00+00:00",
    )
    result = EscalationCapability().recommend(
        EscalationContext(case=_case(events=(event,)))
    )
    assert result.action is EscalationAction.REVIEW
    assert result.status is EscalationStatus.ALREADY_ESCALATED


def test_resolved_case_does_not_escalate():
    result = EscalationCapability().recommend(
        EscalationContext(case=_case(status=CaseStatus.RESOLVED))
    )
    assert result.action is EscalationAction.NONE
    assert result.status is EscalationStatus.NOT_DUE


def test_capability_does_not_claim_external_delivery():
    result = EscalationCapability().recommend(EscalationContext(case=_case()))
    assert "sent" not in result.reason.lower()
    assert "delivered" not in result.reason.lower()
