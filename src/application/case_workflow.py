"""Canonical application orchestration for the Janavani civic workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.domain.authority import Authority
from src.domain.case import Case, CaseStatus
from src.domain.consent import Consent
from src.domain.evidence import Evidence
from src.domain.submission import Submission, SubmissionStatus


class CaseRepository(Protocol):
    def get(self, case_id: str) -> Case | None: ...
    def save(self, case: Case) -> Case: ...


class EvidenceRepository(Protocol):
    def save(self, evidence: Evidence) -> Evidence: ...


class AuthorityRepository(Protocol):
    def get(self, authority_id: str) -> Authority | None: ...


class SubmissionRepository(Protocol):
    def get(self, submission_id: str) -> Submission | None: ...
    def save(self, submission: Submission) -> Submission: ...


@dataclass
class CaseWorkflowService:
    """Coordinate the canonical case lifecycle without provider coupling."""

    cases: CaseRepository
    evidence: EvidenceRepository
    authorities: AuthorityRepository
    submissions: SubmissionRepository | None = None

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

    def create_submission(
        self,
        case_id: str,
        destination_ref: str,
        *,
        consent_ref: str | None = None,
        authorization_ref: str | None = None,
        payload_hash: str | None = None,
        actor: str | None = None,
    ) -> Submission:
        if self.submissions is None:
            raise ValueError("submission repository is not configured")
        case = self._case(case_id)
        if case.status != CaseStatus.APPROVED:
            raise ValueError("submission requires explicit approval")
        if not destination_ref.strip():
            raise ValueError("destination_ref is required")
        submission = Submission(
            case_id=case.id,
            destination_ref=destination_ref.strip(),
            consent_ref=consent_ref,
            authorization_ref=authorization_ref,
            payload_hash=payload_hash,
        )
        case.add_event("submission.created", actor=actor, submission_id=submission.submission_id)
        self.cases.save(case)
        return self.submissions.save(submission)

    def mark_submission_queued(self, submission_id: str, *, actor: str | None = None) -> Submission:
        submission = self._submission(submission_id)
        submission.transition(SubmissionStatus.QUEUED, reason=f"queued by {actor}" if actor else None)
        return self.submissions.save(submission)  # type: ignore[union-attr]

    def mark_submission_transmitting(self, submission_id: str) -> Submission:
        submission = self._submission(submission_id)
        submission.transition(SubmissionStatus.TRANSMITTING)
        return self.submissions.save(submission)  # type: ignore[union-attr]

    def record_submission_sent(self, submission_id: str, *, adapter_id: str, reference: str) -> Submission:
        submission = self._submission(submission_id)
        submission.transition(SubmissionStatus.SENT, adapter_id=adapter_id, reference=reference)
        return self.submissions.save(submission)  # type: ignore[union-attr]

    def record_submission_received(self, submission_id: str, *, adapter_id: str, reference: str) -> Submission:
        submission = self._submission(submission_id)
        submission.transition(SubmissionStatus.RECEIVED, adapter_id=adapter_id, reference=reference)
        return self.submissions.save(submission)  # type: ignore[union-attr]

    def record_submission_acknowledged(self, submission_id: str, *, adapter_id: str, reference: str) -> Submission:
        submission = self._submission(submission_id)
        submission.transition(SubmissionStatus.ACKNOWLEDGED, adapter_id=adapter_id, reference=reference)
        return self.submissions.save(submission)  # type: ignore[union-attr]

    def record_submission_failure(self, submission_id: str, *, reason: str, adapter_id: str | None = None) -> Submission:
        submission = self._submission(submission_id)
        submission.transition(SubmissionStatus.FAILED, adapter_id=adapter_id, reason=reason)
        return self.submissions.save(submission)  # type: ignore[union-attr]

    def _case(self, case_id: str) -> Case:
        case = self.cases.get(case_id)
        if case is None:
            raise ValueError(f"case not found: {case_id}")
        return case

    def _submission(self, submission_id: str) -> Submission:
        if self.submissions is None:
            raise ValueError("submission repository is not configured")
        submission = self.submissions.get(submission_id)
        if submission is None:
            raise ValueError(f"submission not found: {submission_id}")
        return submission
