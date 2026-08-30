"""Shared core-issue analysis and civic-action planning.

The planner decides which capabilities are relevant to a narrated problem. It
may recommend complaint, RTI, or a coordinated sequence; it never submits an
action. Legal/procedural conclusions must come from verified source providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ActionKind(str, Enum):
    COMPLAINT = "complaint"
    RTI = "rti"
    COMPLAINT_AND_RTI = "complaint_and_rti"
    FOLLOW_UP = "follow_up"
    ESCALATION = "escalation"
    EVIDENCE_PRESERVATION = "evidence_preservation"
    PARTY_IN_PERSON_SUPPORT = "party_in_person_support"


@dataclass(frozen=True)
class CivicActionRecommendation:
    action: ActionKind
    priority: int
    reason: str
    depends_on: tuple[ActionKind, ...] = ()


@dataclass(frozen=True)
class CivicActionPlan:
    core_issue: str
    recommendations: tuple[CivicActionRecommendation, ...]
    requires_verified_procedure_check: bool = True


class SharedCivicActionPlanner:
    """Create an action plan from a structured issue assessment."""

    def plan(
        self,
        *,
        core_issue: str,
        needs_service_or_remedy: bool,
        needs_government_information: bool,
        needs_record_or_evidence: bool = False,
        existing_case: bool = False,
    ) -> CivicActionPlan:
        if not core_issue.strip():
            raise ValueError("core_issue is required")

        recommendations: list[CivicActionRecommendation] = []

        if needs_service_or_remedy and needs_government_information:
            recommendations.append(CivicActionRecommendation(
                ActionKind.COMPLAINT_AND_RTI,
                1,
                "The matter appears to require both a remedy and government-held information; assess coordinated complaint and RTI paths.",
            ))
        elif needs_government_information:
            recommendations.append(CivicActionRecommendation(
                ActionKind.RTI,
                1,
                "The immediate need appears to be verified government-held information.",
            ))
        elif needs_service_or_remedy:
            recommendations.append(CivicActionRecommendation(
                ActionKind.FOLLOW_UP if existing_case else ActionKind.COMPLAINT,
                1,
                "The immediate objective appears to be obtaining or following up on a civic service/remedy.",
            ))

        if needs_record_or_evidence:
            recommendations.append(CivicActionRecommendation(
                ActionKind.EVIDENCE_PRESERVATION,
                2,
                "The matter may benefit from preserving relevant records/evidence before further action.",
            ))

        if not recommendations:
            recommendations.append(CivicActionRecommendation(
                ActionKind.COMPLAINT,
                1,
                "A complaint may be appropriate, subject to authority and procedure verification.",
            ))

        return CivicActionPlan(core_issue.strip(), tuple(recommendations))
