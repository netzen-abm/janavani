"""End-to-end shared civic case orchestration.

This composes existing capabilities without making any access surface the owner
of civic logic. It produces a plan; it never submits, emails, posts, or sends a
citizen document externally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from src.core.capabilities.case_decision_engine import SharedCaseDecisionEngine
from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.legal_applicability import SharedLegalApplicability
from src.core.capabilities.civic_action_planner import SharedCivicActionPlanner
from src.core.capabilities.authority_discovery_service import SharedAuthorityDiscovery
from src.core.capabilities.issue_understanding import SharedIssueUnderstanding
from src.core.contracts.case_action_graph import CivicAction
from src.core.contracts.case import Case, CaseStatus


@dataclass(frozen=True)
class CivicCasePlan:
    case: Case
    legal_applicability: object
    action_plan: object
    action_graph: object


class SharedCivicCaseOrchestrator:
    """Compose issue, legal, action and case-graph capabilities."""

    def __init__(self, issue_understanding: SharedIssueUnderstanding, authority_discovery: SharedAuthorityDiscovery):
        self.issue_understanding = issue_understanding
        self.authority_discovery = authority_discovery
        self.legal_applicability = SharedLegalApplicability()
        self.action_planner = SharedCivicActionPlanner()
        self.decision_engine = SharedCaseDecisionEngine()

    def start(self, issue_text: str, *, language: str = "en", jurisdiction: Optional[str] = None, location: Optional[str] = None) -> CivicCasePlan:
        if not issue_text.strip():
            raise ValueError("issue_text is required")

        understanding = self.issue_understanding.understand(issue_text.strip(), language)
        case = Case(
            case_id=f"case-{uuid4().hex[:16]}",
            status=CaseStatus.UNDERSTANDING,
            issue_text=issue_text.strip(),
            metadata={"language": language},
        )
        case.category = understanding.category
        case.department = understanding.department

        authorities = self.authority_discovery.discover(understanding, jurisdiction=jurisdiction, location=location)
        if authorities:
            case.authority = authorities[0].authority
            case.status = CaseStatus.AUTHORITY_VERIFICATION
        else:
            case.status = CaseStatus.AUTHORITY_PENDING

        legal = self.legal_applicability.identify(issue_text, jurisdiction=jurisdiction)
        action_plan = self.action_planner.plan(
            core_issue=issue_text,
            needs_service_or_remedy=True,
            needs_government_information=any(candidate.domain.value == "rti" for candidate in legal.candidates),
        )

        graph = SharedCaseActionGraph()
        for recommendation in action_plan.recommendations:
            if recommendation.action.value == "complaint_and_rti":
                graph.add_action(case.case_id, CivicAction.COMPLAINT)
                graph.add_action(case.case_id, CivicAction.RTI)
            else:
                mapping = {
                    "complaint": CivicAction.COMPLAINT,
                    "rti": CivicAction.RTI,
                    "follow_up": CivicAction.FOLLOW_UP,
                    "escalation": CivicAction.ESCALATION,
                    "evidence_preservation": CivicAction.EVIDENCE_SUPPORT,
                    "party_in_person_support": CivicAction.PARTY_IN_PERSON_SUPPORT,
                }
                graph.add_action(case.case_id, mapping[recommendation.action.value])

        case.touch()
        return CivicCasePlan(case, legal, action_plan, graph.graph(case.case_id))
