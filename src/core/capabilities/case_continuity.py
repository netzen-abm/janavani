"""Shared case-continuity service connecting persistent state and action graph."""

from __future__ import annotations

from datetime import date

from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.case_state import SharedCaseStateRepository
from src.core.capabilities.follow_up_engine import FollowUpRecommendation, SharedFollowUpEngine
from src.core.contracts.case_action_graph import CivicAction, ActionRelation
from src.core.contracts.case_state import CaseLifecycle
from src.core.contracts.follow_up import FollowUpTrigger


class SharedCaseContinuity:
    def __init__(self, state=None, graph=None, follow_up=None):
        self.state = state or SharedCaseStateRepository()
        self.graph = graph or SharedCaseActionGraph()
        self.follow_up = follow_up or SharedFollowUpEngine()

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

    def mark_document_delivered(self, case_id: str, action_id: str, format_name: str):
        if format_name.lower() not in {"pdf", "docx"}:
            raise ValueError("document format must be PDF or DOCX")
        node = self.graph.transition(action_id, "completed")
        self.state.add_event(case_id, "document_delivered", format_name.upper())
        self.state.current_action_id = action_id
        self.state.set_lifecycle(case_id, CaseLifecycle.WAITING_FOR_TRIGGER)
        return node

    def register_follow_up_trigger(self, case_id: str, previous_action_id: str, trigger: FollowUpTrigger, *, reference_date: date) -> FollowUpRecommendation:
        recommendation = self.follow_up.evaluate(trigger, reference_date=reference_date)
        previous = self.graph.get_action(previous_action_id)
        if previous.case_id != case_id:
            raise ValueError("previous action belongs to a different case")
        action = self.graph.add_action(case_id, CivicAction.FOLLOW_UP)
        self.graph.connect(previous, action, ActionRelation.TRIGGERED_BY, trigger=trigger.trigger_id)
        summary = f"follow-up trigger registered: {trigger.trigger_id}"
        if recommendation.due_on:
            summary += f"; due_on={recommendation.due_on.isoformat()}"
        self.state.add_event(case_id, "follow_up_trigger_registered", summary)
        self.state.set_lifecycle(case_id, CaseLifecycle.WAITING_FOR_TRIGGER)
        return recommendation

    def mark_follow_up_due(self, case_id: str, trigger_id: str, *, on: date, recommendation: FollowUpRecommendation):
        if recommendation.trigger_id != trigger_id or not self.follow_up.is_due(recommendation, on=on):
            raise ValueError("follow-up trigger is not due")
        self.state.add_event(case_id, "follow_up_due", trigger_id)
        return self.state.set_lifecycle(case_id, CaseLifecycle.ACTION_READY)

    def wait_for_trigger(self, case_id: str, trigger: str):
        if not trigger.strip():
            raise ValueError("trigger is required")
        self.state.add_event(case_id, "waiting_for_trigger", trigger)
        return self.state.set_lifecycle(case_id, CaseLifecycle.WAITING_FOR_TRIGGER)

    def close(self, case_id: str, summary: str = "Case closed"):
        self.state.add_event(case_id, "case_closed", summary)
        return self.state.set_lifecycle(case_id, CaseLifecycle.CLOSED)
