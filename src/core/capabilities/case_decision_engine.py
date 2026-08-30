"""Shared decision engine for the civic-participation case workflow.

The engine chooses a next-action *candidate* from verified case facts. It never
creates legal conclusions from model memory, invents deadlines, contacts an
authority, or submits a document. Final action selection remains subject to
verified procedure data and explicit citizen choice where required.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.core.capabilities.civic_action_planner import ActionKind


class DecisionConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class VerifiedCaseFacts:
    core_issue: str
    needs_remedy: bool
    needs_information: bool
    existing_case: bool = False
    matter_resolved: bool = False
    verified_procedure_available: bool = False
    verified_next_trigger: Optional[str] = None
    citizen_choice_required: bool = False


@dataclass(frozen=True)
class NextActionDecision:
    action: Optional[ActionKind]
    confidence: DecisionConfidence
    reason: str
    trigger: Optional[str] = None
    requires_user_choice: bool = False
    requires_verified_procedure: bool = True


class SharedCaseDecisionEngine:
    """Determine a safe next civic-action candidate from verified facts."""

    def decide(self, facts: VerifiedCaseFacts) -> NextActionDecision:
        if not facts.core_issue.strip():
            return NextActionDecision(None, DecisionConfidence.INSUFFICIENT, "Core issue is missing.")
        if facts.matter_resolved:
            return NextActionDecision(None, DecisionConfidence.HIGH, "The matter is marked resolved.")
        if not facts.verified_procedure_available:
            return NextActionDecision(
                None,
                DecisionConfidence.INSUFFICIENT,
                "Applicable procedure has not been verified; do not prescribe the next action yet.",
                requires_verified_procedure=True,
            )
        if facts.verified_next_trigger and not facts.existing_case:
            return NextActionDecision(
                None,
                DecisionConfidence.MEDIUM,
                "A procedural trigger is recorded, but the case state must be updated before selecting a follow-up action.",
                trigger=facts.verified_next_trigger,
            )
        if facts.existing_case and facts.verified_next_trigger:
            return NextActionDecision(
                ActionKind.FOLLOW_UP,
                DecisionConfidence.HIGH,
                "A verified follow-up trigger exists for the unresolved case.",
                trigger=facts.verified_next_trigger,
            )
        if facts.needs_remedy and facts.needs_information:
            return NextActionDecision(
                ActionKind.COMPLAINT_AND_RTI,
                DecisionConfidence.HIGH,
                "Verified case facts indicate both a remedy and government-held information are needed.",
            )
        if facts.needs_information:
            return NextActionDecision(
                ActionKind.RTI,
                DecisionConfidence.HIGH,
                "Verified case facts indicate that obtaining government-held information is the immediate objective.",
            )
        if facts.needs_remedy:
            return NextActionDecision(
                ActionKind.FOLLOW_UP if facts.existing_case else ActionKind.COMPLAINT,
                DecisionConfidence.HIGH,
                "Verified case facts indicate a civic remedy/service objective.",
            )
        return NextActionDecision(
            None,
            DecisionConfidence.INSUFFICIENT,
            "The available facts are insufficient to select a civic action safely.",
        )
