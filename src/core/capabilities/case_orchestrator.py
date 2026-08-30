"""Shared orchestration for the first civic-routing vertical slice.

The orchestrator contains workflow semantics only. It is deliberately unaware
of Telegram/WebApp/Mini App rendering and never promotes a citizen-provided
authority to verified status.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from src.core.capabilities.authority_discovery_service import SharedAuthorityDiscovery
from src.core.capabilities.issue_understanding import SharedIssueUnderstanding
from src.core.contracts.case import AuthorityReference, Case, CaseStatus, VerificationStatus


@dataclass(frozen=True)
class CaseRoutingResult:
    case: Case
    authority_candidates: list


class SharedCaseOrchestrator:
    """Coordinate issue understanding, authority discovery and canonical Case state."""

    def __init__(self, issue_understanding: SharedIssueUnderstanding, authority_discovery: SharedAuthorityDiscovery):
        self.issue_understanding = issue_understanding
        self.authority_discovery = authority_discovery

    def start_case(
        self,
        issue_text: str,
        *,
        language: str = "en",
        jurisdiction: Optional[str] = None,
        location: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> CaseRoutingResult:
        if not issue_text or not issue_text.strip():
            raise ValueError("issue_text is required")

        case = Case(
            case_id=case_id or f"case-{uuid4().hex[:16]}",
            status=CaseStatus.UNDERSTANDING,
            issue_text=issue_text.strip(),
            metadata={"language": language},
        )

        understanding = self.issue_understanding.understand(issue_text.strip(), language)
        case.category = understanding.category
        case.department = understanding.department
        case.status = CaseStatus.AUTHORITY_PENDING
        case.touch()

        candidates = self.authority_discovery.discover(
            understanding,
            jurisdiction=jurisdiction,
            location=location,
        )

        if candidates:
            best = candidates[0].authority
            case.authority = best
            case.status = (
                CaseStatus.AUTHORITY_VERIFICATION
                if best.verification != VerificationStatus.VERIFIED
                else CaseStatus.REVIEW
            )
        else:
            case.status = CaseStatus.AUTHORITY_PENDING
        case.touch()

        return CaseRoutingResult(case=case, authority_candidates=candidates)

    @staticmethod
    def accept_citizen_authority(case: Case, authority: AuthorityReference) -> Case:
        """Attach a citizen-supplied authority as pending, never verified."""
        if authority.source != "citizen_provided":
            raise ValueError("Citizen authority input must use source='citizen_provided'")
        pending = AuthorityReference(
            authority_id=authority.authority_id,
            name=authority.name,
            location=authority.location,
            source="citizen_provided",
            verification=VerificationStatus.PENDING,
        )
        case.set_authority(pending)
        return case
