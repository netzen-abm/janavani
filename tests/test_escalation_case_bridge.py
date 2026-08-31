import pytest

from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.escalation_action_service import EscalationActionProposal
from src.core.capabilities.escalation_case_bridge import SharedEscalationCaseBridge
from src.core.contracts.case_action_graph import CivicAction


def test_verified_escalation_proposal_becomes_case_action():
    graph = SharedCaseActionGraph()
    previous = graph.add_action("case-1", CivicAction.COMPLAINT, status="completed")
    proposal = EscalationActionProposal("escalation", "route-1", "auth-2", "Next Authority", "verified route")
    link = SharedEscalationCaseBridge().add_proposal(graph, case_id="case-1", previous_action_id=previous.action_id, proposal=proposal)
    assert link.case_id == "case-1"
    assert graph.get_action(link.action_id).action == CivicAction.ESCALATION
    assert link.requires_user_confirmation is True


def test_cross_case_previous_action_is_rejected():
    graph = SharedCaseActionGraph()
    previous = graph.add_action("case-1", CivicAction.COMPLAINT, status="completed")
    proposal = EscalationActionProposal("escalation", "route-1", "auth-2", "Next Authority", "verified route")
    with pytest.raises(ValueError):
        SharedEscalationCaseBridge().add_proposal(graph, case_id="case-2", previous_action_id=previous.action_id, proposal=proposal)
