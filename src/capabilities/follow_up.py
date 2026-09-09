"""Provider- and surface-neutral adaptive follow-up capability.

Follow-up is derived from canonical Case state and history. It recommends
user-controlled next steps; it never sends, submits, or asserts external
 delivery.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.civic_case import CaseStatus, CivicCase


class FollowUpAction(str, Enum):
    REMINDER = "reminder"
    FOLLOW_UP_LETTER = "follow_up_letter"
    RTI = "rti"
    REVIEW_RTI_RESPONSE = "review_rti_response"
    DEPARTMENT_HEAD = "department_head"
    ADMINISTRATIVE_HEAD = "administrative_head"
    LEGISLATOR = "legislator"
    BSA_RELATED = "bsa_related"
    PARTY_IN_PERSON = "party_in_person"
    CLOSE = "close"


class FollowUpStatus(str, Enum):
    DUE = "follow_up_due"
    SCHEDULED = "reminder_scheduled"
    USER_ACTION_PENDING = "user_action_pending"
    USER_ACTION_REPORTED = "user_action_reported"
    RESPONSE_PENDING = "response_pending"
    RESPONSE_RECEIVED = "response_received"
    RESPONSE_SATISFACTORY = "response_satisfactory"
    RESPONSE_UNSATISFACTORY = "response_unsatisfactory"
    ESCALATION_RECOMMENDED = "escalation_recommended"
    CLOSED = "closed"


@dataclass(frozen=True)
class FollowUpContext:
    """Canonical case-derived context for follow-up decisioning."""

    case: CivicCase
    response_status: str | None = None
    user_report: str | None = None


@dataclass(frozen=True)
class FollowUpRecommendation:
    action: FollowUpAction
    status: FollowUpStatus
    reason: str


class FollowUpCapability:
    """Shared adaptive follow-up decision capability."""

    def recommend(self, context: FollowUpContext) -> FollowUpRecommendation:
        case = context.case
        response = (context.response_status or "").strip().lower()
        events = {event.event_type.value for event in case.events}

        if case.status is CaseStatus.CLOSED:
            return FollowUpRecommendation(
                FollowUpAction.CLOSE,
                FollowUpStatus.CLOSED,
                "The canonical case is already closed.",
            )

        if case.status is CaseStatus.RESOLVED:
            return FollowUpRecommendation(
                FollowUpAction.CLOSE,
                FollowUpStatus.RESPONSE_SATISFACTORY,
                "The canonical case is resolved and can be closed by the user.",
            )

        if response in {"satisfactory", "resolved"}:
            return FollowUpRecommendation(
                FollowUpAction.CLOSE,
                FollowUpStatus.RESPONSE_SATISFACTORY,
                "The user reported a satisfactory or resolved outcome.",
            )

        if response in {"unsatisfactory", "incomplete", "inadequate"}:
            action = (
                FollowUpAction.BSA_RELATED
                if case.case_type.value == "rti"
                else FollowUpAction.ADMINISTRATIVE_HEAD
            )
            return FollowUpRecommendation(
                action,
                FollowUpStatus.ESCALATION_RECOMMENDED,
                "The user reported an unsatisfactory or incomplete response.",
            )

        if response in {"received", "pending_review"}:
            return FollowUpRecommendation(
                FollowUpAction.REVIEW_RTI_RESPONSE,
                FollowUpStatus.RESPONSE_RECEIVED,
                "A response was reported and should be reviewed by the user.",
            )

        if case.case_type.value == "rti" and case.status in {
            CaseStatus.SUBMITTED,
            CaseStatus.ACKNOWLEDGED,
            CaseStatus.FOLLOW_UP,
            CaseStatus.IN_PROGRESS,
        }:
            return FollowUpRecommendation(
                FollowUpAction.REMINDER,
                FollowUpStatus.RESPONSE_PENDING,
                "Follow up on the expected RTI response.",
            )

        if case.status in {
            CaseStatus.ACKNOWLEDGED,
            CaseStatus.IN_PROGRESS,
            CaseStatus.RESPONDED,
        }:
            if "follow_up" not in events:
                return FollowUpRecommendation(
                    FollowUpAction.FOLLOW_UP_LETTER,
                    FollowUpStatus.DUE,
                    "The case is eligible for a user-controlled follow-up action.",
                )
            if "escalated" not in events:
                return FollowUpRecommendation(
                    FollowUpAction.ADMINISTRATIVE_HEAD,
                    FollowUpStatus.ESCALATION_RECOMMENDED,
                    "A follow-up has been recorded; consider the next authority level.",
                )

        return FollowUpRecommendation(
            FollowUpAction.REMINDER,
            FollowUpStatus.DUE,
            "No stronger next action can be inferred safely from the canonical case state.",
        )
