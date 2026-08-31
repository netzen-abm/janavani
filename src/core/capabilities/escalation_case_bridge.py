"""Bridge verified escalation proposals into the shared case action graph."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.escalation_action_service import EscalationActionProposal
from src.core.contracts.case_action_graph import ActionRelation, CivicAction


@dataclass(frozen=True)
class EscalationCaseLink:
    action_id: str
    case_id: str
    route_id: str
    authority_id: str
    requires_user_confirmation: bool


class SharedEscalationCaseBridge:
    def add_proposal(
        self,
        graph: SharedCaseActionGraph,
        *,
        case_id: str,
        previous_action_id: str,
        proposal: EscalationActionProposal,
    ) -> EscalationCaseLink:
        previous = graph.get_action(previous_action_id)
        if previous.case_id != case_id:
            raise ValueError("previous action does not belong to case")
        action = graph.add_action(case_id, CivicAction.ESCALATION, status="planned")
        graph.connect(previous, action, ActionRelation.FOLLOWS, trigger=proposal.route_id)
        return EscalationCaseLink(
            action.action_id,
            case_id,
            proposal.route_id,
            proposal.authority_id,
            proposal.requires_user_confirmation,
        )
