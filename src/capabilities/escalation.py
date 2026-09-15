"""Provider- and surface-neutral escalation decision capability.

Escalation is a user-controlled decision derived from canonical Case state and
history. This capability does not persist, mutate, submit, or transport an
escalation. Authority discovery and verified-channel selection remain separate
capabilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.civic_case import CaseStatus, CivicCase


class EscalationAction(str, Enum):
    NONE = "none"
    FOLLOW_UP = "follow_up"
    ADMINISTRATIVE_HEAD = "administrative_head"
    LEGISLATOR = "legislator"
    REVIEW = "review"


class EscalationStatus(str, Enum):
    NOT_DUE = "not_due"
    RECOMMENDED = "recommended"
    ALREADY_ESCALATED = "already_escalated"
    USER_ACTION_REQUIRED = "user_action_required"


@dataclass(frozen=True)
class EscalationContext:
    """Canonical case-derived context for escalation decisioning."""

    case: CivicCase
    user_report: str | None = None


@dataclass(frozen=True)
class EscalationRecommendation:
    action: EscalationAction
    status: EscalationStatus
    reason: str


class EscalationCapability:
    """Shared escalation decision boundary; never performs external effects."""

    def recommend(self, context: EscalationContext) -> EscalationRecommendation:
        case = context.case
        report = (context.user_report or "").strip().lower()
        events = {event.event_type.value for event in case.events}

        if case.status in {CaseStatus.CLOSED, CaseStatus.RESOLVED}:
            return EscalationRecommendation(
                EscalationAction.NONE,
                EscalationStatus.NOT_DUE,
                "A closed or resolved case does not require escalation.",
            )

        if "escalated" in events:
            return EscalationRecommendation(
                EscalationAction.REVIEW,
                EscalationStatus.ALREADY_ESCALATED,
                "An escalation event is already present in the canonical case history.",
            )

        if report in {"satisfactory", "resolved"}:
            return EscalationRecommendation(
                EscalationAction.NONE,
                EscalationStatus.NOT_DUE,
                "The user reported a satisfactory or resolved outcome.",
            )

        if report in {"unsatisfactory", "incomplete", "inadequate"}:
            return EscalationRecommendation(
                EscalationAction.ADMINISTRATIVE_HEAD,
                EscalationStatus.RECOMMENDED,
                "The user reported an unsatisfactory or incomplete outcome.",
            )

        if case.status in {
            CaseStatus.FOLLOW_UP,
            CaseStatus.RESPONDED,
            CaseStatus.IN_PROGRESS,
        } and "follow_up" in events:
            return EscalationRecommendation(
                EscalationAction.ADMINISTRATIVE_HEAD,
                EscalationStatus.USER_ACTION_REQUIRED,
                "A follow-up has been recorded without a satisfactory resolution.",
            )

        return EscalationRecommendation(
            EscalationAction.FOLLOW_UP,
            EscalationStatus.NOT_DUE,
            "Follow-up should precede escalation unless canonical evidence indicates otherwise.",
        )
