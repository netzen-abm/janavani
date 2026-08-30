from datetime import date

from src.core.capabilities.followup_escalation import FollowUpStage, SharedFollowUpEscalation


def test_reference_is_case_scoped():
    service = SharedFollowUpEscalation()
    ref = service.issue_reference("case-123", issued_on=date(2026, 8, 30))
    assert ref.case_id == "case-123"
    assert ref.reference_id.startswith("JV-20260830-")


def test_unresolved_case_gets_followup_plan():
    service = SharedFollowUpEscalation()
    ref = service.issue_reference("case-123", issued_on=date(2026, 8, 30))
    plan = service.plan_follow_up(ref, issue_nature="broken public road", submitted_on=date(2026, 8, 30))
    assert plan.next_stage == FollowUpStage.FOLLOW_UP
    assert plan.document_type == "follow_up_letter"
    assert plan.suggested_after == date(2026, 9, 14)
    assert plan.user_action_required is True


def test_resolved_case_stops_followup():
    service = SharedFollowUpEscalation()
    ref = service.issue_reference("case-123", issued_on=date(2026, 8, 30))
    plan = service.plan_follow_up(ref, issue_nature="water issue", unresolved=False)
    assert plan.next_stage == FollowUpStage.CLOSED
    assert plan.suggested_after is None
