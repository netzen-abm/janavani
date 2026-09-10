"""Canonical, provider- and surface-neutral submission capability.

Document generation remains separate from external submission. This capability
only submits an already-reviewed document after authentication, authorization,
valid consent, and explicit user approval have all been satisfied.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.access.consent import ConsentRepositoryReader, ConsentRequirement, require_consent
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.core.civic_case import CivicCase
from src.core.submission import SubmissionRecord, SubmissionRepository
from src.identity.context import IdentityContext

CAPABILITY_ID = "case:submit"
CONSENT_PURPOSE = "case_submission"


@dataclass(frozen=True)
class SubmissionRequest:
    case_id: str
    document_id: str
    destination_ref: str
    consent_scope: str
    source_channel: str | None = None


@dataclass(frozen=True)
class SubmissionReceipt:
    """Evidence returned by a transport only when the destination accepted it."""

    acknowledgement_ref: str | None = None
    notes: str | None = None


class SubmissionTransport(Protocol):
    """External transport adapter; it is never the domain authority."""

    def send(self, *, case: CivicCase, document_id: str, destination_ref: str) -> SubmissionReceipt:
        ...


class SubmissionCapability:
    """Shared submission boundary consumed by every access surface."""

    def __init__(self, case_capability: CivicCaseCapability,
                 consent_repository: ConsentRepositoryReader,
                 transport: SubmissionTransport,
                 submission_repository: SubmissionRepository | None = None) -> None:
        self._cases = case_capability
        self._consents = consent_repository
        self._transport = transport
        self._submissions = submission_repository

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _save(self, record: SubmissionRecord) -> SubmissionRecord:
        if self._submissions is not None:
            self._submissions.save(record)
        return record

    def submit(self, request: SubmissionRequest, *, identity: IdentityContext,
               explicit_user_approval: bool) -> CivicCaseResult:
        """Submit an attached document only after every consequential-action gate."""
        case = self._cases.get_owned(request.case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if request.document_id not in case.document_refs:
            raise ValueError("Document is not attached to the case")
        if not request.destination_ref.strip():
            raise ValueError("A submission destination is required")
        if not explicit_user_approval:
            raise PermissionError("Explicit user approval is required for submission")

        decision = authorize(AuthorizationRequest(
            context=identity, capability=CAPABILITY_ID, action="case:submit", resource_id=case.case_id
        ))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to submit this case")

        require_consent(self._consents, ConsentRequirement(
            subject_id=identity.principal.principal_id,
            purpose=CONSENT_PURPOSE,
            scope=request.consent_scope,
        ))

        now = self._now()
        submission = SubmissionRecord.new(
            submission_id=f"sub_{uuid4().hex}",
            case_id=case.case_id,
            destination_ref=request.destination_ref,
            document_ref=request.document_id,
            channel=request.source_channel or "shared",
        )
        self._save(submission)

        # Persist the attempt before external I/O. If transport fails, the
        # durable record remains explicit and no false success is claimed.
        submission = replace(
            submission,
            state="submitting",
            attempted_at=now,
            updated_at=now,
        )
        self._save(submission)
        self._cases.transition(
            request.case_id, action="case:begin_submission", identity=identity,
            source_channel=request.source_channel,
        )

        try:
            receipt = self._transport.send(
                case=case, document_id=request.document_id, destination_ref=request.destination_ref
            )
        except Exception as exc:
            failed = replace(
                submission,
                state="failed",
                error_code=type(exc).__name__,
                retry_count=submission.retry_count + 1,
                updated_at=self._now(),
            )
            self._save(failed)
            raise

        submitted_at = self._now()
        submission = replace(
            submission,
            state="submitted",
            submitted_at=submitted_at,
            external_reference=receipt.acknowledgement_ref,
            updated_at=submitted_at,
        )
        self._save(submission)
        self._cases.transition(
            request.case_id, action="case:submit", identity=identity,
            source_channel=request.source_channel,
        )

        if receipt.acknowledgement_ref:
            acknowledged_at = self._now()
            self._save(replace(
                submission,
                state="acknowledged",
                acknowledged_at=acknowledged_at,
                ack_ref=receipt.acknowledgement_ref,
                updated_at=acknowledged_at,
            ))
            self._cases.transition(
                request.case_id, action="case:acknowledge", identity=identity,
                source_channel=request.source_channel, source_ref=receipt.acknowledgement_ref,
                notes=receipt.notes,
            )

        final_case = self._cases.get_owned(request.case_id, identity=identity)
        if final_case is None:
            raise LookupError("Case not found after submission")
        return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)
