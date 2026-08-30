"""Shared case-continuity service connecting persistent state and action graph."""

from __future__ import annotations

from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.case_state import SharedCaseStateRepository
from src.core.contracts.case_action_graph import CivicAction
from src.core.contracts.case_state import CaseLifecycle


class SharedCaseContinuity:
    def __init__(self, state: SharedCaseStateRepository | None = None, graph: SharedCaseActionGraph | None = None):
        self.state = state or SharedCaseStateRepository()
        self.graph = graph or SharedCaseActionGraph()

    def start_case(self, reference_number: str):
        return self.state.create(reference_number)

    def plan_action(self, case_id: str, action: CivicAction):
        node = self.graph.add_action(case_id, action)
        self.state.add_event(case_id, "action_planned", action.value)
        self.state.set_lifecycle(case_id, CaseLifecycle.ACTION_READY)
        return node

    def complete_action(self, case_id: str, action_id: str, summary: str):
        node = self.graph.transition(action_id, "completed")
        self.state.add_event(case_id, "action_completed", summary)
        self.state.current_action_id = action_id
        return node

    def wait_for_trigger(self, case_id: str, trigger: str):
        if not trigger.strip():
            raise ValueError("trigger is required")
        self.state.add_event(case_id, "waiting_for_trigger", trigger)
        return self.state.set_lifecycle(case_id, CaseLifecycle.WAITING_FOR_TRIGGER)

    def close(self, case_id: str, summary: str = "Case closed"):
        self.state.add_event(case_id, "case_closed", summary)
        return self.state.set_lifecycle(case_id, CaseLifecycle.CLOSED)
