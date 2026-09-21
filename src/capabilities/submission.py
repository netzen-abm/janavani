"""Canonical, provider- and surface-neutral submission capability."""
from __future__ import annotations

from datetime import datetime, timezone

from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.capabilities.submission_contract import (
    SubmissionOutcomeUnknown, SubmissionReceipt, SubmissionRequest,
    SubmissionTransport,
)
from src.capabilities.submission_flow import submit as submit_request
from src.capabilities.submission_security import SubmissionSecurity
from src.capabilities.submission_state import SubmissionState
from src.core.evidence import EvidenceRepository
from src.core.submission import SubmissionRepository
from src.identity.context import IdentityContext
from src.storage.repositories.submission_case_transaction import (
    SubmissionCaseTransactionRepository,
)

CAPABILITY_ID = "case:submit"
CONSENT_PURPOSE = "case_submission"
ACKNOWLEDGEMENT_EVIDENCE_TYPE = "submission_acknowledgement"


class SubmissionCapability:
    """Stable public façade; flow, security, state and delivery stay modular."""

    def __init__(
        self, case_capability: CivicCaseCapability,
        consent_repository,
        transport: SubmissionTransport | None = None,
        submission_repository: SubmissionRepository | None = None, *,
        delivery_transport=None, artifact_resolver=None,
        evidence_repository: EvidenceRepository | None = None,
        submission_case_transaction_repository: (
            SubmissionCaseTransactionRepository | None
        ) = None,
    ) -> None:
        if transport is None and delivery_transport is None:
            raise ValueError("A submission transport is required")
        if delivery_transport is not None and artifact_resolver is None:
            raise ValueError("An artifact resolver is required for delivery transport")
        self._cases = case_capability
        self._consents = consent_repository
        self._transport = transport
        self._submissions = submission_repository
        self._delivery_transport = delivery_transport
        self._artifact_resolver = artifact_resolver
        self._evidence = evidence_repository
        self._atomic = submission_case_transaction_repository
        self._state = SubmissionState(self)
        self._security = SubmissionSecurity(self)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _save(self, record, *, expected_version=None):
        return self._state.save(record, expected_version)

    def _reserve(self, submission):
        return self._state.reserve(submission)

    def _with_submitting(self, submission):
        return self._state.with_submitting(submission)

    def _mark_submitted(self, submission, external_ref, request, identity, context):
        return self._state.mark_submitted(
            submission, external_ref, request, identity, context
        )

    def _atomic_case_mutation(self, **kwargs):
        return self._state.atomic_mutation(**kwargs)

    def _acknowledgement_evidence(self, case, evidence_id):
        return self._state.acknowledgement_evidence(case, evidence_id)

    def _acknowledge(self, **kwargs):
        return self._state.acknowledge(**kwargs)

    def _consequential_submission_decision(self, **kwargs):
        return self._security.decision(**kwargs)

    @staticmethod
    def _validate_execution_context(
        execution_context, identity, *, action, resource_id=None
    ):
        return SubmissionSecurity.validate(
            execution_context, identity, action=action, resource_id=resource_id
        )

    @staticmethod
    def _child_case_context(parent, identity, case_id, action):
        return SubmissionSecurity.child_context(parent, identity, case_id, action)

    def submit(
        self, request: SubmissionRequest, *, identity: IdentityContext,
        explicit_user_approval: bool, execution_context=None,
    ) -> CivicCaseResult:
        case = submit_request(
            self, request, identity=identity,
            explicit_user_approval=explicit_user_approval,
            execution_context=execution_context,
        )
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def acknowledge_with_evidence(
        self, submission_id, *, evidence_id, identity,
        notes=None, source_channel=None, execution_context=None,
    ):
        self._validate_execution_context(
            execution_context, identity, action="case:acknowledge"
        )
        if self._submissions is None:
            raise RuntimeError("Submission repository is required")
        submission = self._submissions.get(submission_id)
        if submission is None:
            raise LookupError("Submission not found")
        case = self._cases.get_owned(submission.case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if submission.state != "submitted":
            raise ValueError("Only a submitted submission can be acknowledged")
        self._acknowledge(
            case=case, submission=submission, evidence_id=evidence_id,
            identity=identity, source_channel=source_channel,
            notes=notes, execution_context=execution_context,
        )
        final_case = self._cases.get_owned(case.case_id, identity=identity)
        if final_case is None:
            raise LookupError("Case not found after acknowledgement")
        return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)
