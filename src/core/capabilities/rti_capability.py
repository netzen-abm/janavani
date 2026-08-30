"""Shared RTI capability.

This capability distinguishes information-seeking from grievance/remedy paths,
keeps RTI connected to the canonical Case, and prepares only a reviewed
DocumentDraft. It never files, emails, posts, or submits an RTI.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.core.capabilities.document_preparation import DocumentDraft
from src.core.contracts.case import Case, VerificationStatus


class RTIAction(str, Enum):
    NOT_INDICATED = "not_indicated"
    RTI_FIRST = "rti_first"
    COMPLAINT_FIRST_THEN_RTI = "complaint_first_then_rti"
    COMPLAINT_AND_RTI = "complaint_and_rti"
    RTI_AFTER_TRIGGER = "rti_after_trigger"


@dataclass(frozen=True)
class RTIAssessment:
    action: RTIAction
    reason: str
    information_objective: str
    procedure_check_required: bool = True


@dataclass(frozen=True)
class RTIRequestPlan:
    authority_name: str
    authority_address: str
    authority_email: Optional[str]
    questions: tuple[str, ...]
    subject: str


class SharedRTICapability:
    """Assess and prepare an RTI request without submission behavior."""

    def assess(
        self,
        *,
        information_objective: str,
        remedy_needed: bool,
        information_needed: bool,
        existing_complaint: bool = False,
    ) -> RTIAssessment:
        if not information_objective.strip():
            raise ValueError("information_objective is required")
        if not information_needed:
            return RTIAssessment(RTIAction.NOT_INDICATED, "No government-held information objective was identified.", information_objective)
        if remedy_needed and existing_complaint:
            return RTIAssessment(RTIAction.RTI_AFTER_TRIGGER, "An existing complaint may need an information track if the verified procedural trigger occurs.", information_objective)
        if remedy_needed:
            return RTIAssessment(RTIAction.COMPLAINT_AND_RTI, "The matter appears to contain both a remedy and information objective.", information_objective)
        return RTIAssessment(RTIAction.RTI_FIRST, "The primary objective appears to be obtaining government-held information.", information_objective)

    def prepare_plan(
        self,
        case: Case,
        *,
        authority_name: str,
        authority_address: str,
        authority_email: Optional[str],
        questions: tuple[str, ...],
        subject: str,
    ) -> RTIRequestPlan:
        if not case.case_id:
            raise ValueError("case_id is required")
        if not case.authority or case.authority.verification != VerificationStatus.VERIFIED:
            raise ValueError("A verified public authority is required before RTI preparation")
        if not questions:
            raise ValueError("At least one information question is required")
        return RTIRequestPlan(
            authority_name=authority_name.strip(),
            authority_address=authority_address.strip(),
            authority_email=authority_email.strip() if authority_email else None,
            questions=tuple(q.strip() for q in questions if q.strip()),
            subject=subject.strip(),
        )
