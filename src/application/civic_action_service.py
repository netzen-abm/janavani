"""Application service for the first channel-neutral civic-action vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.domain import Case, CaseType
from src.domain.authority import AuthorityReference
from src.domain.evidence import Evidence
from src.domain.workflow import CivicActionWorkflow, WorkflowStage


@dataclass(slots=True)
class CivicActionService:
    """Coordinate domain objects without depending on a transport or provider."""

    def create_case(
        self,
        *,
        subject: str,
        narrative: str = "",
        actor_id: Optional[str] = None,
        case_type: CaseType = CaseType.COMPLAINT,
        jurisdiction: Optional[str] = None,
    ) -> CivicActionWorkflow:
        case = Case(
            case_type=case_type,
            created_by=actor_id,
            subject=subject.strip(),
            narrative=narrative.strip(),
            jurisdiction=jurisdiction,
        )
        workflow = CivicActionWorkflow(case)
        workflow.advance(WorkflowStage.UNDERSTANDING, actor_id=actor_id)
        return workflow

    def attach_evidence(
        self,
        workflow: CivicActionWorkflow,
        evidence: Evidence,
        *,
        actor_id: Optional[str] = None,
    ) -> Evidence:
        workflow.case.add_evidence(evidence.evidence_id, actor_id=actor_id)
        workflow.advance(WorkflowStage.EVIDENCE, actor_id=actor_id)
        return evidence

    def attach_authority(
        self,
        workflow: CivicActionWorkflow,
        authority: AuthorityReference,
        *,
        actor_id: Optional[str] = None,
    ) -> AuthorityReference:
        workflow.case.related_office_id = authority.office_id
        workflow.case.add_event(
            "AUTHORITY_ATTACHED",
            actor_id=actor_id,
            source_ref=authority.authority_id,
            notes="Authority reference attached; source verification remains explicit.",
        )
        workflow.advance(WorkflowStage.AUTHORITY, actor_id=actor_id)
        return authority

    def prepare_review(self, workflow: CivicActionWorkflow, *, actor_id: Optional[str] = None) -> None:
        workflow.advance(WorkflowStage.ACTION, actor_id=actor_id)
        workflow.advance(WorkflowStage.REVIEW, actor_id=actor_id)

    def approve_for_submission(self, workflow: CivicActionWorkflow, *, actor_id: str) -> None:
        if not actor_id.strip():
            raise ValueError("actor_id is required for citizen approval")
        workflow.case.add_event(
            "CITIZEN_APPROVED",
            actor_id=actor_id,
            notes="Citizen explicitly approved the case for submission.",
        )
        workflow.advance(WorkflowStage.SUBMISSION, actor_id=actor_id)

    def begin_tracking(self, workflow: CivicActionWorkflow, *, actor_id: Optional[str] = None) -> None:
        workflow.advance(WorkflowStage.TRACKING, actor_id=actor_id)
