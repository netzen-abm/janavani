"""Acceptance scenarios for the canonical civic-routing model.

These tests deliberately use verified facts at the decision boundary. Natural
language extraction is tested separately; the decision engine must never infer
legal/procedural facts merely because a word appeared in the narrative.
"""

from src.core.capabilities.case_decision_engine import (
    DecisionConfidence,
    SharedCaseDecisionEngine,
    VerifiedCaseFacts,
)
from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.contracts.case_action_graph import ActionRelation, CivicAction
from src.core.capabilities.civic_action_planner import ActionKind


def verified(**kwargs):
    base = dict(
        core_issue="public service matter",
        needs_remedy=False,
        needs_information=False,
        verified_procedure_available=True,
    )
    base.update(kwargs)
    return VerifiedCaseFacts(**base)


def test_rti_first():
    decision = SharedCaseDecisionEngine().decide(verified(needs_information=True))
    assert decision.action == ActionKind.RTI
    assert decision.confidence == DecisionConfidence.HIGH


def test_complaint_first_then_rti():
    engine = SharedCaseDecisionEngine()
    first = engine.decide(verified(needs_remedy=True))
    later = engine.decide(verified(needs_information=True, existing_case=True, verified_next_trigger="verified RTI trigger"))
    assert first.action == ActionKind.COMPLAINT
    assert later.action == ActionKind.FOLLOW_UP
    assert later.trigger == "verified RTI trigger"


def test_complaint_and_rti_together():
    decision = SharedCaseDecisionEngine().decide(verified(needs_remedy=True, needs_information=True))
    assert decision.action == ActionKind.COMPLAINT_AND_RTI


def test_case_graph_can_hold_parallel_complaint_and_rti():
    graph = SharedCaseActionGraph()
    complaint = graph.add_action("case-parallel", CivicAction.COMPLAINT)
    rti = graph.add_action("case-parallel", CivicAction.RTI)
    graph.connect(complaint, rti, ActionRelation.PARALLEL)
    assert {n.action for n in graph.next_actions("case-parallel")} == {CivicAction.COMPLAINT, CivicAction.RTI}


def test_unverified_procedure_blocks_prescription():
    decision = SharedCaseDecisionEngine().decide(
        verified(needs_remedy=True, verified_procedure_available=False)
    )
    assert decision.action is None
    assert decision.confidence == DecisionConfidence.INSUFFICIENT
