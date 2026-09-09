from src.capabilities.follow_up import (
    FollowUpAction,
    FollowUpCapability,
    FollowUpContext,
    FollowUpStatus,
)
from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase


def _case(case_type=CaseType.COMPLAINT, status=CaseStatus.ACKNOWLEDGED, events=()):
    return CivicCase(
        case_id="case-test",
        case_type=case_type,
        subject="Test matter",
        narrative="Test narrative",
        created_by="citizen:test",
        status=status,
        events=list(events),
    )


def test_letter_case_recommends_user_controlled_follow_up():
    result = FollowUpCapability().recommend(FollowUpContext(case=_case()))
    assert result.action is FollowUpAction.FOLLOW_UP_LETTER
    assert result.status is FollowUpStatus.DUE


def test_rti_submitted_recommends_response_reminder():
    result = FollowUpCapability().recommend(
        FollowUpContext(case=_case(CaseType.RTI, CaseStatus.SUBMITTED))
    )
    assert result.action is FollowUpAction.REMINDER
    assert result.status is FollowUpStatus.RESPONSE_PENDING


def test_rti_received_recommends_review():
    result = FollowUpCapability().recommend(
        FollowUpContext(
            case=_case(CaseType.RTI, CaseStatus.ACKNOWLEDGED),
            response_status="received",
        )
    )
    assert result.action is FollowUpAction.REVIEW_RTI_RESPONSE
    assert result.status is FollowUpStatus.RESPONSE_RECEIVED


def test_unsatisfactory_rti_recommends_bsa_related_next_step():
    result = FollowUpCapability().recommend(
        FollowUpContext(
            case=_case(CaseType.RTI),
            response_status="unsatisfactory",
        )
    )
    assert result.action is FollowUpAction.BSA_RELATED
    assert result.status is FollowUpStatus.ESCALATION_RECOMMENDED


def test_satisfactory_outcome_can_close():
    result = FollowUpCapability().recommend(
        FollowUpContext(case=_case(), response_status="satisfactory")
    )
    assert result.action is FollowUpAction.CLOSE
    assert result.status is FollowUpStatus.RESPONSE_SATISFACTORY


def test_existing_follow_up_recommends_escalation():
    events = (
        CaseEvent(
            event_id="event-follow-up",
            case_id="case-test",
            event_type=CaseEventType.FOLLOW_UP,
            occurred_at="2026-09-09T00:00:00+00:00",
        ),
    )
    result = FollowUpCapability().recommend(FollowUpContext(case=_case(events=events)))
    assert result.action is FollowUpAction.ADMINISTRATIVE_HEAD
    assert result.status is FollowUpStatus.ESCALATION_RECOMMENDED


def test_closed_case_stays_closed():
    result = FollowUpCapability().recommend(
        FollowUpContext(case=_case(status=CaseStatus.CLOSED))
    )
    assert result.action is FollowUpAction.CLOSE
    assert result.status is FollowUpStatus.CLOSED


def test_recommendation_never_claims_delivery():
    result = FollowUpCapability().recommend(FollowUpContext(case=_case()))
    assert "sent" not in result.reason.lower()
    assert "delivered" not in result.reason.lower()
