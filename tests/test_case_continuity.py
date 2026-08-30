from src.core.capabilities.case_continuity import SharedCaseContinuity
from src.core.contracts.case_action_graph import CivicAction
from src.core.contracts.case_state import CaseLifecycle


def test_action_lifecycle_updates_case_state_and_graph():
    service = SharedCaseContinuity()
    case = service.start_case("JV-20260830-ABC123")
    action = service.plan_action(case.reference.case_id, CivicAction.COMPLAINT)
    assert case.reference.lifecycle == CaseLifecycle.ACTION_READY
    service.complete_action(case.reference.case_id, action.action_id, "Complaint document delivered to citizen")
    assert service.graph.graph(case.reference.case_id).nodes[0].status == "completed"
    assert service.state.get(case.reference.case_id).events[-1].event_type == "action_completed"


def test_waiting_trigger_and_close_are_recorded():
    service = SharedCaseContinuity()
    case = service.start_case("JV-20260830-ABC123")
    service.wait_for_trigger(case.reference.case_id, "verified procedural event")
    assert service.state.get(case.reference.case_id).reference.lifecycle == CaseLifecycle.WAITING_FOR_TRIGGER
    service.close(case.reference.case_id, "Citizen reports resolution")
    assert service.state.get(case.reference.case_id).reference.lifecycle == CaseLifecycle.CLOSED
