"""Channel-neutral follow-up planning for CivicCase workflows."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


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
    RESPONSE_PENDING = "response_pending"
    RESPONSE_RECEIVED = "response_received"
    RESPONSE_SATISFACTORY = "response_satisfactory"
    RESPONSE_UNSATISFACTORY = "response_unsatisfactory"
    ESCALATION_RECOMMENDED = "escalation_recommended"
    CLOSED = "closed"


@dataclass(frozen=True)
class FollowUpContext:
    case_type: str
    documents: tuple[str, ...] = field(default_factory=tuple)
    completed_actions: tuple[str, ...] = field(default_factory=tuple)
    response_status: str | None = None
    user_report: str | None = None


@dataclass(frozen=True)
class FollowUpRecommendation:
    action: FollowUpAction
    status: FollowUpStatus
    reason: str


def recommend_follow_up(context: FollowUpContext) -> FollowUpRecommendation:
    """Return a conservative next step from explicit case context.

    This function recommends; it never submits, sends, or asserts delivery.
    """
    documents = {item.lower() for item in context.documents}
    actions = {item.lower() for item in context.completed_actions}
    response = (context.response_status or "").lower()

    if "rti" in documents or "rti" in actions:
        if response in {"satisfactory", "resolved"}:
            return FollowUpRecommendation(
                FollowUpAction.CLOSE,
                FollowUpStatus.RESPONSE_SATISFACTORY,
                "User-reported RTI outcome is satisfactory or resolved.",
            )
        if response in {"unsatisfactory", "incomplete", "inadequate"}:
            return FollowUpRecommendation(
                FollowUpAction.BSA_RELATED,
                FollowUpStatus.ESCALATION_RECOMMENDED,
                "User reports that the RTI response is unsatisfactory or incomplete.",
            )
        if response in {"received", "pending_review"}:
            return FollowUpRecommendation(
                FollowUpAction.REVIEW_RTI_RESPONSE,
                FollowUpStatus.RESPONSE_RECEIVED,
                "An RTI response has been reported and should be reviewed.",
            )
        return FollowUpRecommendation(
            FollowUpAction.REMINDER,
            FollowUpStatus.RESPONSE_PENDING,
            "Follow up on the expected RTI response.",
        )

    if "follow_up_letter" in actions:
        return FollowUpRecommendation(
            FollowUpAction.ADMINISTRATIVE_HEAD,
            FollowUpStatus.ESCALATION_RECOMMENDED,
            "A follow-up letter has already been recorded; consider the next authority level.",
        )

    if "letter" in documents:
        if "department_head" not in actions:
            return FollowUpRecommendation(
                FollowUpAction.FOLLOW_UP_LETTER,
                FollowUpStatus.DUE,
                "A letter exists and may require a user-controlled follow-up.",
            )
        if "administrative_head" not in actions:
            return FollowUpRecommendation(
                FollowUpAction.ADMINISTRATIVE_HEAD,
                FollowUpStatus.ESCALATION_RECOMMENDED,
                "The department-level step has been recorded; consider the administrative level.",
            )
        if "legislator" not in actions:
            return FollowUpRecommendation(
                FollowUpAction.LEGISLATOR,
                FollowUpStatus.ESCALATION_RECOMMENDED,
                "Administrative follow-up has been recorded; consider the appropriate legislator.",
            )

    return FollowUpRecommendation(
        FollowUpAction.REMINDER,
        FollowUpStatus.DUE,
        "No stronger next action can be inferred safely from the recorded context.",
    )
