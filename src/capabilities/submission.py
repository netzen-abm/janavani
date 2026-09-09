"""Canonical, provider- and surface-neutral submission capability.

Document generation remains separate from external submission. This capability
only submits an already-reviewed document after authentication, authorization,
valid consent, and explicit user approval have all been satisfied.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.access.consent import ConsentRepositoryReader, ConsentRequirement, require_consent
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.core.civic_case import CivicCase
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

    def send(
        self,
        *,
        case: CivicCase,
        document_id: str,
        destination_ref: str,
    ) -> SubmissionReceipt:
        ...


class SubmissionCapability:
    """Shared submission boundary consumed by every access surface."""

    def __init__(
        self,
        case_capability: CivicCaseCapability,
        consent_repository: ConsentRepositoryReader,
        transport: SubmissionTransport,
    ) -> None:
        self._cases = case_capability
        self._consents = consent_repository
        self._transport = transport

    def submit(
        self,
        request: SubmissionRequest,
        *,
        identity: IdentityContext,
        explicit_user_approval: bool,
    ) -> CivicCaseResult:
        """Submit a reviewed document only after every consequential-action gate."""
        case = self._cases.get_owned(request.case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if request.document_id not in case.document_refs:
            raise ValueError("Document is not attached to the case")
        if not request.destination_ref.strip():
            raise ValueError("A submission destination is required")
        if not explicit_user_approval:
            raise PermissionError("Explicit user approval is required for submission")

        decision = authorize(
            AuthorizationRequest(
                context=identity,
                capability=CAPABILITY_ID,
                action="case:submit",
                resource_id=case.case_id,
            )
        )
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to submit this case")

        require_consent(
            self._consents,
            ConsentRequirement(
                subject_id=identity.principal.principal_id,
                purpose=CONSENT_PURPOSE,
                scope=request.consent_scope,
            ),
        )

        self._cases.transition(
            request.case_id,
            action="case:begin_submission",
            identity=identity,
            source_channel=request.source_channel,
        )
        try:
            receipt = self._transport.send(
                case=case,
                document_id=request.document_id,
                destination_ref=request.destination_ref,
            )
        except Exception:
            # Leave the case in SUBMITTING. No external acknowledgement means
            # Janavani must not claim that submission succeeded.
            self._cases._repository.save(case)
            raise

        self._cases.transition(
            request.case_id,
            action="case:submit",
            identity=identity,
            source_channel=request.source_channel,
            explicit_user_approval=True,
        )
        if receipt.acknowledgement_ref:
            self._cases.transition(
                request.case_id,
                action="case:acknowledge",
                identity=identity,
                source_channel=request.source_channel,
                source_ref=receipt.acknowledgement_ref,
                notes=receipt.notes,
            )
        return self._cases.get_owned(request.case_id, identity=identity) and CivicCaseResult(
            self._cases.get_owned(request.case_id, identity=identity),
            AuthorizationDecision.ALLOW,
        )
