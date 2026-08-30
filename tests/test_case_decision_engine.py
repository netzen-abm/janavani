from src.core.capabilities.case_decision_engine import (
    DecisionConfidence,
    SharedCaseDecisionEngine,
    VerifiedCaseFacts,
)
from src.core.capabilities.civic_action_planner import ActionKind


def test_information_only_case_selects_rti():
    result = SharedCaseDecisionEngine().decide(VerifiedCaseFacts(
        core_issue="need government records",
        needs_remedy=False,
        needs_information=True,
        verified_procedure_available=True,
    ))
    assert result.action == ActionKind.RTI
    assert result.confidence == DecisionConfidence.HIGH


def test_remedy_and_information_select_parallel_action():
    result = SharedCaseDecisionEngine().decide(VerifiedCaseFacts(
        core_issue="public work not completed and records needed",
        needs_remedy=True,
        needs_information=True,
        verified_procedure_available=True,
    ))
    assert result.action == ActionKind.COMPLAINT_AND_RTI


def test_unverified_procedure_blocks_action():
    result = SharedCaseDecisionEngine().decide(VerifiedCaseFacts(
        core_issue="unresolved public service",
        needs_remedy=True,
        needs_information=False,
        verified_procedure_available=False,
    ))
    assert result.action is None
    assert result.confidence == DecisionConfidence.INSUFFICIENT


def test_verified_followup_trigger_advances_existing_case():
    result = SharedCaseDecisionEngine().decide(VerifiedCaseFacts(
        core_issue="unresolved complaint",
        needs_remedy=True,
        needs_information=False,
        existing_case=True,
        verified_procedure_available=True,
        verified_next_trigger="response period elapsed",
    ))
    assert result.action == ActionKind.FOLLOW_UP
    assert result.trigger == "response period elapsed"
