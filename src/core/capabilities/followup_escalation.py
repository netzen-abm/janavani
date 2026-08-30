"""Shared civic follow-up and escalation planning capability.

This capability plans the next lawful civic-action document from the case's
nature, status and elapsed time. It does not contact authorities, submit forms,
or send reminders externally. It produces a local plan and document intent;
the access surface decides how to present the plan to the citizen.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4


class FollowUpStage(str, Enum):
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    ADMINISTRATIVE_ESCALATION = "administrative_escalation"
    LEGISLATIVE_REPRESENTATION = "legislative_representation"
    RTI = "rti"
    RTI_FIRST_APPEAL = "rti_first_appeal"
    RTI_SECOND_APPEAL = "rti_second_appeal"
    EVIDENCE_PRESERVATION = "evidence_preservation"
    PARTY_IN_PERSON_SUPPORT = "party_in_person_support"
    CLOSED = "closed"


@dataclass(frozen=True)
class FollowUpReference:
    reference_id: str
    case_id: str
    issued_on: date


@dataclass(frozen=True)
class FollowUpPlan:
    reference: FollowUpReference
    current_stage: FollowUpStage
    next_stage: Optional[FollowUpStage]
    suggested_after: Optional[date]
    reason: str
    document_type: Optional[str] = None
    authority_role: Optional[str] = None
    user_action_required: bool = True


class SharedFollowUpEscalation:
    """Plan follow-up/escalation without becoming a submission or legal agent."""

    def issue_reference(self, case_id: str, *, issued_on: Optional[date] = None) -> FollowUpReference:
        if not case_id.strip():
            raise ValueError("case_id is required")
        return FollowUpReference(
            reference_id=f"JV-{date.today().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
            case_id=case_id,
            issued_on=issued_on or date.today(),
        )

    def plan_follow_up(
        self,
        reference: FollowUpReference,
        *,
        issue_nature: str,
        current_stage: FollowUpStage = FollowUpStage.INITIAL,
        submitted_on: Optional[date] = None,
        unresolved: bool = True,
        urgent: bool = False,
    ) -> FollowUpPlan:
        if not issue_nature.strip():
            raise ValueError("issue_nature is required")
        if not unresolved:
            return FollowUpPlan(reference, current_stage, FollowUpStage.CLOSED, None, "Citizen indicates the matter is resolved.")

        base = submitted_on or reference.issued_on
        if current_stage == FollowUpStage.INITIAL:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.FOLLOW_UP,
                base + timedelta(days=7 if urgent else 15),
                "Prepare a follow-up representation if the matter remains unresolved.",
                document_type="follow_up_letter",
            )
        if current_stage == FollowUpStage.FOLLOW_UP:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.ADMINISTRATIVE_ESCALATION,
                base + timedelta(days=15 if urgent else 30),
                "Prepare an escalation to the next appropriate administrative authority.",
                document_type="escalation_letter",
                authority_role="next_administrative_authority",
            )
        if current_stage == FollowUpStage.ADMINISTRATIVE_ESCALATION:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.LEGISLATIVE_REPRESENTATION,
                base + timedelta(days=30),
                "Consider a representation to the appropriate elected representative where appropriate.",
                document_type="legislative_representation",
                authority_role="appropriate_legislator",
            )
        if current_stage == FollowUpStage.LEGISLATIVE_REPRESENTATION:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.RTI,
                None,
                "If the issue requires government-held information, consider an RTI request.",
                document_type="rti_application",
                authority_role="public_information_officer",
            )
        if current_stage == FollowUpStage.RTI:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.RTI_FIRST_APPEAL,
                None,
                "If the RTI response is absent or unsatisfactory, assess whether a first appeal is appropriate.",
                document_type="rti_first_appeal",
                authority_role="first_appellate_authority",
            )
        if current_stage == FollowUpStage.RTI_FIRST_APPEAL:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.RTI_SECOND_APPEAL,
                None,
                "If the first appeal does not resolve the information issue, assess the applicable second-appeal route.",
                document_type="rti_second_appeal",
                authority_role="information_commission",
            )
        if current_stage == FollowUpStage.RTI_SECOND_APPEAL:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.EVIDENCE_PRESERVATION,
                None,
                "Where digital evidence is material, consider evidence-preservation support before any further legal step.",
                document_type="evidence_preservation_request",
            )
        if current_stage == FollowUpStage.EVIDENCE_PRESERVATION:
            return FollowUpPlan(
                reference, current_stage, FollowUpStage.PARTY_IN_PERSON_SUPPORT,
                None,
                "If self-representation is appropriate, provide party-in-person procedural information and document support.",
                document_type="party_in_person_support_pack",
            )
        return FollowUpPlan(reference, current_stage, None, None, "No automatic next step is prescribed.")
