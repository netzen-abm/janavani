"""Canonical, provider- and surface-neutral submission capability."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest
from src.access.consequential import ConsequentialDecision, ConsequentialOperationRequest, gate_consequential_operation
from src.access.consent import ConsentRepositoryReader, ConsentRequirement
from src.access.execution_consent import ExecutionConsentRequirement, require_execution_consent
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.core.civic_case import CaseEvent, CaseEventType, CivicCase
from src.core.evidence import EvidenceRepository
from src.core.execution import CapabilityExecutionContext
from src.core.submission import SubmissionRecord, SubmissionRepository
from src.delivery.contract import (
    DeliveryArtifactResolver,
    DeliveryOutcome,
    DeliveryRequest,
    DeliveryTransport,
    DeliveryTransportError,
)
from src.identity.context import IdentityContext
from src.storage.repositories.submission_case_transaction import SubmissionCaseTransactionRepository

CAPABILITY_ID = "case:submit"
CONSENT_PURPOSE = "case_submission"
ACKNOWLEDGEMENT_EVIDENCE_TYPE = "submission_acknowledgement"


@dataclass(frozen=True)
class SubmissionRequest:
    case_id: str
    document_id: str
    destination_ref: str
    consent_scope: str
    source_channel: str | None = None
    artifact_id: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True)
class SubmissionReceipt:
    """Legacy transport result; acknowledgement requires independent evidence."""
    acknowledgement_ref: str | None = None
    notes: str | None = None


class SubmissionTransport(Protocol):
    def send(self, *, case: CivicCase, document_id: str, destination_ref: str) -> SubmissionReceipt: ...


class SubmissionOutcomeUnknown(RuntimeError):
    """External delivery outcome is ambiguous and requires reconciliation."""


class SubmissionCapability:
    """Shared submission boundary consumed by every access surface."""

    def __init__(self, case_capability: CivicCaseCapability,
                 consent_repository: ConsentRepositoryReader,
                 transport: SubmissionTransport | None = None,
                 submission_repository: SubmissionRepository | None = None,
                 *, delivery_transport: DeliveryTransport | None = None,
                 artifact_resolver: DeliveryArtifactResolver | None = None,
                 evidence_repository: EvidenceRepository | None = None,
                 submission_case_transaction_repository: SubmissionCaseTransactionRepository | None = None) -> None:
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

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _event_id(submission: SubmissionRecord, stage: str) -> str:
        digest = sha256(f"{submission.idempotency_key}:{stage}".encode()).hexdigest()[:32]
        return f"event-submission-{stage}-{digest}"

    def _save(self, record: SubmissionRecord, *, expected_version: int | None = None) -> SubmissionRecord:
        if self._submissions is None:
            return record
        if expected_version is None:
            self._submissions.save(record)
        else:
            self._submissions.update_if_version(record, expected_version=expected_version)
        return record

    def _reserve(self, submission: SubmissionRecord) -> tuple[SubmissionRecord, bool]:
        if self._submissions is None:
            return submission, False
        return self._submissions.create_idempotent(submission)

    def _acknowledgement_evidence(self, case: CivicCase, evidence_id: str) -> None:
        if self._evidence is None:
            raise PermissionError("Independent acknowledgement evidence repository is required")
        evidence = self._evidence.get(evidence_id)
        if evidence is None:
            raise LookupError("Acknowledgement evidence was not found")
        if evidence_id not in case.evidence_refs:
            raise PermissionError("Acknowledgement evidence is not attached to the case")
        if evidence.evidence_type != ACKNOWLEDGEMENT_EVIDENCE_TYPE:
            raise ValueError("Evidence is not an acknowledgement record")
        if evidence.status != "ACTIVE":
            raise ValueError("Acknowledgement evidence is not active")

    @staticmethod
    def _synchronize_case_projection(target: CivicCase, projection: CivicCase) -> None:
        """Copy the committed projection into the caller object after success only."""
        for field_name, value in projection.__dict__.items():
            setattr(target, field_name, deepcopy(value))

    def _atomic_case_mutation(self, *, submission: SubmissionRecord, expected_submission_version: int,
                              case: CivicCase, expected_case_version: int, action: str,
                              identity: IdentityContext, source_channel: str | None,
                              source_ref: str | None = None, notes: str | None = None) -> None:
        if self._atomic is None:
            raise RuntimeError("Atomic Submission-Case repository is required")
        now = self._now()
        event_id = self._event_id(submission, action.removeprefix("case:"))
        event_type = {"case:begin_submission": CaseEventType.SUBMITTING,
                      "case:submit": CaseEventType.SUBMITTED,
                      "case:acknowledge": CaseEventType.ACKNOWLEDGED}[action]
        event = CaseEvent(event_id=event_id, case_id=case.case_id, event_type=event_type,
                          occurred_at=now, actor_id=identity.principal.principal_id,
                          source_channel=source_channel, source_ref=source_ref, notes=notes)
        projection = deepcopy(case)
        if action == "case:begin_submission":
            projection.begin_submission(event_id=event_id, occurred_at=now,
                                        actor_id=identity.principal.principal_id, source_channel=source_channel)
        elif action == "case:submit":
            projection.submit(event_id=event_id, occurred_at=now,
                              actor_id=identity.principal.principal_id, source_channel=source_channel)
        elif action == "case:acknowledge":
            projection.acknowledge(event_id=event_id, occurred_at=now,
                                   actor_id=identity.principal.principal_id, source_channel=source_channel,
                                   source_ref=source_ref, notes=notes)
        else:
            raise ValueError(f"Unsupported atomic Submission-Case action: {action}")
        self._atomic.persist_mutation(submission=submission, expected_submission_version=expected_submission_version,
                                      case=projection, expected_case_version=expected_case_version, event=event,
                                      idempotency_key=event_id)
        self._synchronize_case_projection(case, projection)

    def _acknowledge(self, *, case: CivicCase, submission: SubmissionRecord, evidence_id: str,
                     identity: IdentityContext, source_channel: str | None, notes: str | None,
                     execution_context: CapabilityExecutionContext | None = None) -> None:
        self._acknowledgement_evidence(case, evidence_id)
        acknowledged_at = self._now()
        expected_case_version = case.version
        updated = replace(submission, state="acknowledged", acknowledged_at=acknowledged_at,
                          ack_ref=evidence_id, updated_at=acknowledged_at, version=submission.version + 1)
        if self._atomic is not None:
            self._validate_execution_context(execution_context, identity, action="case:acknowledge", resource_id=case.case_id)
            self._atomic_case_mutation(submission=updated, expected_submission_version=submission.version,
                                       case=case, expected_case_version=expected_case_version,
                                       action="case:acknowledge", identity=identity,
                                       source_channel=source_channel, source_ref=evidence_id, notes=notes)
        else:
            self._save(updated, expected_version=submission.version)
            self._cases.transition(case.case_id, action="case:acknowledge", identity=identity,
                                   source_channel=source_channel, source_ref=evidence_id, notes=notes,
                                   execution_context=self._child_case_context(execution_context, identity,
                                                                              case.case_id, "case:acknowledge"))

    def _consequential_submission_decision(self, *, identity: IdentityContext, case_id: str,
                                           consent_scope: str, explicit_user_approval: bool,
                                           execution_context: CapabilityExecutionContext | None,
                                           idempotency_key: str) -> ConsequentialDecision:
        if execution_context is None:
            execution_context = CapabilityExecutionContext.for_capability(
                identity, capability_id=CAPABILITY_ID, action="case:submit", surface="shared",
                resource_id=case_id, side_effect_class="external_side_effect",
                idempotency_key=idempotency_key)
        elif execution_context.idempotency_key != idempotency_key:
            raise ValueError("Execution idempotency key does not match the Submission idempotency key")
        requirement = ConsentRequirement(subject_id=identity.principal.principal_id,
                                         purpose=CONSENT_PURPOSE, scope=consent_scope)
        request = ConsequentialOperationRequest(
            authorization=AuthorizationRequest(context=identity, capability=CAPABILITY_ID,
                action="case:submit", resource_id=case_id, requires_approval=True,
                execution_context=execution_context),
            execution_context=execution_context, consent_requirement=requirement,
            explicit_user_approval=explicit_user_approval)
        if execution_context.identity.principal.principal_id != identity.principal.principal_id:
            raise PermissionError("Execution identity does not match the authenticated identity")
        require_execution_consent(self._consents, ExecutionConsentRequirement(requirement), execution_context)
        return gate_consequential_operation(request, consent_repository=self._consents)

    def submit(self, request: SubmissionRequest, *, identity: IdentityContext,
               explicit_user_approval: bool,
               execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="case:submit", resource_id=request.case_id)
        case = self._cases.get_owned(request.case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if request.document_id not in case.document_refs:
            raise ValueError("Document is not attached to the case")
        if not request.destination_ref.strip():
            raise ValueError("A submission destination is required")
        key = request.idempotency_key or (execution_context.idempotency_key if execution_context is not None else None) or f"subreq_{uuid4().hex}"
        decision = self._consequential_submission_decision(identity=identity, case_id=case.case_id,
            consent_scope=request.consent_scope, explicit_user_approval=explicit_user_approval,
            execution_context=execution_context, idempotency_key=key)
        if decision is ConsequentialDecision.DENY:
            raise PermissionError("Identity is not authorized to submit this case")
        if decision is ConsequentialDecision.CONSENT_REQUIRED:
            raise PermissionError("Explicit consent is required for submission")
        if decision is ConsequentialDecision.REQUIRE_APPROVAL:
            raise PermissionError("Explicit user approval is required for submission")
        proposed = SubmissionRecord.new(submission_id=f"sub_{uuid4().hex}", case_id=case.case_id,
                                         destination_ref=request.destination_ref, document_ref=request.document_id,
                                         channel=request.source_channel or "shared", idempotency_key=key)
        if self._atomic is not None and self._submissions is not None:
            submission = self._submissions.get_by_idempotency_key(key)
            replay = submission is not None
            if submission is None:
                self._atomic_case_mutation(submission=replace(proposed, state="submitting"),
                                           expected_submission_version=0, case=case,
                                           expected_case_version=case.version, action="case:begin_submission",
                                           identity=identity, source_channel=request.source_channel)
                submission = replace(proposed, state="submitting")
            elif submission.state in {"submitted", "acknowledged"}:
                final_case = self._cases.get_owned(request.case_id, identity=identity)
                if final_case is None:
                    raise LookupError("Case not found after idempotent replay")
                return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)
            elif submission.state == "unknown":
                raise RuntimeError("Submission already exists for this idempotency key and requires reconciliation")
            elif submission.state not in {"failed", "submitting"}:
                raise RuntimeError(f"Submission is not retryable: {submission.state}")
        else:
            submission, replay = self._reserve(proposed)
            if replay:
                if submission.state in {"submitted", "acknowledged"}:
                    final_case = self._cases.get_owned(request.case_id, identity=identity)
                    if final_case is None:
                        raise LookupError("Case not found after idempotent replay")
                    return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)
                if submission.state in {"submitting", "unknown"}:
                    raise RuntimeError("Submission already exists for this idempotency key and requires reconciliation")
                if submission.state != "failed":
                    raise RuntimeError(f"Submission is not retryable: {submission.state}")
        if submission.state == "created":
            submitting = replace(submission, state="submitting", attempted_at=self._now(),
                                 updated_at=self._now(), version=submission.version + 1)
            self._save(submitting, expected_version=submission.version)
            if self._atomic is None:
                self._cases.transition(request.case_id, action="case:begin_submission", identity=identity,
                                       source_channel=request.source_channel,
                                       execution_context=self._child_case_context(execution_context, identity,
                                                                                  request.case_id, "case:begin_submission"))
            submission = submitting
        elif submission.state == "failed":
            submitting = replace(submission, state="submitting", attempted_at=self._now(),
                                 updated_at=self._now(), version=submission.version + 1)
            self._save(submitting, expected_version=submission.version)
            submission = submitting
        elif submission.state != "submitting":
            raise RuntimeError(f"Unsupported submission state: {submission.state}")
        if self._delivery_transport is not None:
            try:
                if request.artifact_id is None:
                    raise ValueError("An approved artifact is required for delivery")
                assert self._artifact_resolver is not None
                artifact = self._artifact_resolver.resolve(artifact_id=request.artifact_id, case_id=case.case_id,
                                                           document_id=request.document_id)
            except Exception as exc:
                failed = replace(submission, state="failed", error_code=type(exc).__name__,
                                 retry_count=submission.retry_count + 1, updated_at=self._now(), version=submission.version + 1)
                self._save(failed, expected_version=submission.version)
                raise
            try:
                delivery_receipt = self._delivery_transport.deliver(DeliveryRequest(
                    submission_id=submission.submission_id, idempotency_key=submission.idempotency_key,
                    case_id=case.case_id, document_id=request.document_id, destination_ref=request.destination_ref,
                    channel=request.source_channel or "shared", artifact=artifact))
            except DeliveryTransportError as exc:
                if exc.outcome is DeliveryOutcome.UNKNOWN:
                    unknown = replace(submission, state="unknown", error_code="unknown_transport_outcome",
                                      updated_at=self._now(), version=submission.version + 1)
                    self._save(unknown, expected_version=submission.version)
                    raise SubmissionOutcomeUnknown("Delivery outcome is unknown; reconciliation is required") from exc
                failed = replace(submission, state="failed", error_code=type(exc).__name__,
                                 retry_count=submission.retry_count + 1, updated_at=self._now(), version=submission.version + 1)
                self._save(failed, expected_version=submission.version)
                raise
            except Exception as exc:
                unknown = replace(submission, state="unknown", error_code="unknown_transport_outcome",
                                  updated_at=self._now(), version=submission.version + 1)
                self._save(unknown, expected_version=submission.version)
                raise SubmissionOutcomeUnknown("Delivery outcome is unknown; reconciliation is required") from exc
            if delivery_receipt.outcome is DeliveryOutcome.UNKNOWN:
                unknown = replace(submission, state="unknown", error_code="unknown_transport_outcome",
                                  updated_at=self._now(), version=submission.version + 1)
                self._save(unknown, expected_version=submission.version)
                raise SubmissionOutcomeUnknown("Delivery outcome is unknown; reconciliation is required")
            if delivery_receipt.outcome is DeliveryOutcome.FAILED:
                failed = replace(submission, state="failed", error_code="delivery_failed",
                                 retry_count=submission.retry_count + 1, updated_at=self._now(), version=submission.version + 1)
                self._save(failed, expected_version=submission.version)
                raise RuntimeError("Delivery transport reported failure")
            external_reference = delivery_receipt.external_reference
            evidence_id = delivery_receipt.acknowledgement_evidence_ref
            notes = delivery_receipt.notes
        else:
            assert self._transport is not None
            try:
                receipt = self._transport.send(case=case, document_id=request.document_id,
                                               destination_ref=request.destination_ref)
            except Exception as exc:
                failed = replace(submission, state="failed", error_code=type(exc).__name__,
                                 retry_count=submission.retry_count + 1, updated_at=self._now(), version=submission.version + 1)
                self._save(failed, expected_version=submission.version)
                raise
            external_reference = receipt.acknowledgement_ref
            evidence_id = None
            notes = receipt.notes
        submitted_at = self._now()
        submitted = replace(submission, state="submitted", submitted_at=submitted_at,
                            external_reference=external_reference, updated_at=submitted_at, version=submission.version + 1)
        if self._atomic is not None and self._submissions is not None:
            fresh_case = self._cases.get_owned(request.case_id, identity=identity)
            if fresh_case is None:
                raise LookupError("Case not found before atomic submission outcome")
            expected_case_version = fresh_case.version
            self._atomic_case_mutation(submission=submitted, expected_submission_version=submission.version,
                                       case=fresh_case, expected_case_version=expected_case_version,
                                       action="case:submit", identity=identity, source_channel=request.source_channel)
        else:
            self._save(submitted, expected_version=submission.version)
            self._cases.transition(request.case_id, action="case:submit", identity=identity,
                                   source_channel=request.source_channel,
                                   execution_context=self._child_case_context(execution_context, identity,
                                                                              request.case_id, "case:submit"))
        if evidence_id:
            acknowledged_case = self._cases.get_owned(request.case_id, identity=identity)
            if acknowledged_case is None:
                raise LookupError("Case not found before acknowledgement")
            self._acknowledge(case=acknowledged_case, submission=submitted, evidence_id=evidence_id,
                              identity=identity, source_channel=request.source_channel, notes=notes,
                              execution_context=execution_context)
        final_case = self._cases.get_owned(request.case_id, identity=identity)
        if final_case is None:
            raise LookupError("Case not found after submission")
        return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)

    def acknowledge_with_evidence(self, submission_id: str, *, evidence_id: str,
                                  identity: IdentityContext, notes: str | None = None,
                                  source_channel: str | None = None,
                                  execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="case:acknowledge")
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
        self._acknowledge(case=case, submission=submission, evidence_id=evidence_id, identity=identity,
                          source_channel=source_channel, notes=notes, execution_context=execution_context)
        final_case = self._cases.get_owned(case.case_id, identity=identity)
        if final_case is None:
            raise LookupError("Case not found after acknowledgement")
        return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)

    @staticmethod
    def _validate_execution_context(execution_context: CapabilityExecutionContext | None,
                                    identity: IdentityContext, *, action: str, resource_id: str | None = None) -> None:
        if execution_context is None:
            return
        if execution_context.identity.principal.principal_id != identity.principal.principal_id:
            raise PermissionError("Execution identity does not match the authenticated identity")
        if execution_context.capability_id != CAPABILITY_ID:
            raise ValueError("Execution capability does not match the Submission capability")
        if execution_context.action != action:
            raise ValueError("Execution action does not match the Submission operation")
        if resource_id is not None and execution_context.resource_id != resource_id:
            raise ValueError("Execution resource does not match the Submission resource")

    @staticmethod
    def _child_case_context(parent: CapabilityExecutionContext | None, identity: IdentityContext,
                            case_id: str, action: str) -> CapabilityExecutionContext | None:
        if parent is None:
            return None
        return CapabilityExecutionContext.for_capability(
            identity, capability_id="JNV-CIVIC-COMPLAINT", action=action, surface=parent.surface,
            resource_id=case_id, correlation_id=parent.correlation_id, parent_operation_id=parent.operation_id,
            authorization_ref=parent.authorization_ref, consent_refs=parent.consent_refs,
            policy_ref=parent.policy_ref, risk_level=parent.risk_level, side_effect_class=parent.side_effect_class,
            provenance=parent.provenance, metadata=parent.metadata,
        )
