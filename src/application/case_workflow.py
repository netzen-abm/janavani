"""Canonical application orchestration for the Janavani civic workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from src.domain.authority import Authority
from src.domain.case import Case, CaseStatus
from src.domain.consent import Consent
from src.domain.evidence import Evidence


class CaseRepository(Protocol):
    def get(self, case_id: str) -> Case | None: ...
    def save(self, case: Case) -> Case: ...


class EvidenceRepository(Protocol):
    def save(self, evidence: Evidence) -> Evidence: ...


class AuthorityRepository(Protocol):
    def get(self, authority_id: str) -> Authority | None: ...


@dataclass
class InMemoryCaseRepository:
    """Deterministic repository used by application tests and local composition."""

    cases: dict[str, Case] = field(default_factory=dict)

    def get(self, case_id: str) -> Case | None:
        return self.cases.get(case_id)

    def save(self, case: Case) -> Case:
        self.cases[case.id] = case
        return case


@dataclass
class InMemoryEvidenceRepository:
    evidence: dict[str, Evidence] = field(default_factory=dict)

    def save(self, evidence: Evidence) -> Evidence:
        self.evidence[evidence.evidence_id] = evidence
        return evidence


@dataclass
class CaseWorkflowService:
    """Coordinate the canonical case lifecycle without provider coupling."""

    cases: CaseRepository
    evidence: EvidenceRepository
    authorities: AuthorityRepository

    def create_case(self, issue: str, *, actor: str | None = None) -> Case:
        case = Case(issue=issue)
        case.add_event("case.created", actor=actor)
        return self.cases.save(case)

    def attach_evidence(self, case_id: str, evidence: Evidence, *, actor: str | None = None) -> Case:
        case = self._case(case_id)
        if evidence.case_id != case.id:
            raise ValueError("evidence belongs to a different case")
        self.evidence.save(evidence)
        case.attach_evidence(evidence.evidence_id, actor=actor)
        if case.status == CaseStatus.OPEN:
            case.transition(CaseStatus.EVIDENCE_COLLECTION, actor=actor)
        return self.cases.save(case)

    def select_authority(self, case_id: str, authority_id: str, *, actor: str | None = None) -> Case:
        case = self._case(case_id)
        if self.authorities.get(authority_id) is None:
            raise ValueError("authority not found")
        if authority_id not in case.authority_ids:
            case.authority_ids.append(authority_id)
        case.add_event("case.authority_selected", actor=actor, authority_id=authority_id)
        case.transition(CaseStatus.AUTHORITY_SELECTION, actor=actor)
        return self.cases.save(case)

    def record_consent(self, case_id: str, consent: Consent, *, actor: str | None = None) -> Case:
        case = self._case(case_id)
        if consent.subject_id != case.id:
            raise ValueError("consent subject does not match case")
        if not consent.is_active():
            raise ValueError("consent is not active")
        if consent.consent_id not in case.consent_ids:
            case.consent_ids.append(consent.consent_id)
        case.add_event("case.consent_recorded", actor=actor, consent_id=consent.consent_id, capability_id=consent.capability_id)
        return self.cases.save(case)

    def request_submission_approval(self, case_id: str, *, actor: str | None = None) -> Case:
        case = self._case(case_id)
        if not case.evidence_ids:
            raise ValueError("submission approval requires evidence references")
        if not case.authority_ids:
            raise ValueError("submission approval requires an authority reference")
        case.transition(CaseStatus.REVIEW, actor=actor)
        case.add_event("submission.approval_requested", actor=actor)
        return self.cases.save(case)

    def approve_submission(self, case_id: str, *, actor: str | None = None) -> Case:
        case = self._case(case_id)
        if case.status != CaseStatus.REVIEW:
            raise ValueError("case is not awaiting submission approval")
        case.transition(CaseStatus.APPROVED, actor=actor)
        case.add_event("submission.approved", actor=actor)
        return self.cases.save(case)

    def mark_submission_started(self, case_id: str, *, actor: str | None = None) -> Case:
        case = self._case(case_id)
        if case.status != CaseStatus.APPROVED:
            raise ValueError("submission requires explicit approval")
        case.transition(CaseStatus.SUBMISSION, actor=actor)
        case.add_event("submission.started", actor=actor)
        return self.cases.save(case)

    def _case(self, case_id: str) -> Case:
        case = self.cases.get(case_id)
        if case is None:
            raise ValueError(f"case not found: {case_id}")
        return case
