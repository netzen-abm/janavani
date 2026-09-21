"""Canonical, provider- and surface-neutral submission capability."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256

from src.access.authorization import AuthorizationDecision, AuthorizationRequest
from src.access.consequential import (
    ConsequentialOperationRequest, gate_consequential_operation,
)
from src.access.consent import ConsentRepositoryReader, ConsentRequirement
from src.access.execution_consent import (
    ExecutionConsentRequirement, require_execution_consent,
)
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.capabilities.submission_contract import (
    SubmissionOutcomeUnknown, SubmissionReceipt, SubmissionRequest,
    SubmissionTransport,
)
from src.core.civic_case import CaseEvent, CaseEventType
from src.core.evidence import EvidenceRepository
from src.core.execution import CapabilityExecutionContext
from src.core.submission import SubmissionRepository
from src.identity.context import IdentityContext
from src.storage.repositories.submission_case_transaction import (
    SubmissionCaseTransactionRepository,
)
from src.capabilities.submission_flow import submit as submit_request

CAPABILITY_ID = "case:submit"
CONSENT_PURPOSE = "case_submission"
ACKNOWLEDGEMENT_EVIDENCE_TYPE = "submission_acknowledgement"


class SubmissionCapability:
    """Shared submission boundary consumed by every access surface."""

    def __init__(
        self, case_capability: CivicCaseCapability,
        consent_repository: ConsentRepositoryReader,
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

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _event_id(submission, stage):
        digest = sha256(
            f"{submission.idempotency_key}:{stage}".encode()
        ).hexdigest()[:32]
        return f"event-submission-{stage}-{digest}"

    def _save(self, record, *, expected_version=None):
        if self._submissions is None:
            return record
        if expected_version is None:
            self._submissions.save(record)
        else:
            self._submissions.update_if_version(record, expected_version=expected_version)
        return record

    def _reserve(self, submission):
        if self._submissions is None:
            return submission, False
        return self._submissions.create_idempotent(submission)

    def _with_submitting(self, submission):
        now = self._now()
        return replace(
            submission, state="submitting", attempted_at=now,
            updated_at=now, version=submission.version + 1,
        )

    def _mark_submitted(self, submission, external_ref, request, identity, context):
        now = self._now()
        updated = replace(
            submission, state="submitted", submitted_at=now,
            external_reference=external_ref, updated_at=now,
            version=submission.version + 1,
        )
        if self._atomic is not None and self._submissions is not None:
            case = self._cases.get_owned(request.case_id, identity=identity)
            if case is None:
                raise LookupError("Case not found before atomic submission outcome")
            self._atomic_case_mutation(
                submission=updated, expected_submission_version=submission.version,
                case=case, expected_case_version=case.version,
                action="case:submit", identity=identity,
                source_channel=request.source_channel,
            )
        else:
            self._save(updated, expected_version=submission.version)
            self._cases.transition(
                request.case_id, action="case:submit", identity=identity,
                source_channel=request.source_channel,
                execution_context=self._child_case_context(
                    context, identity, request.case_id, "case:submit"
                ),
            )
        return updated

    def _acknowledgement_evidence(self, case, evidence_id):
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

    def _atomic_case_mutation(
        self, *, submission, expected_submission_version, case,
        expected_case_version, action, identity, source_channel,
        source_ref=None, notes=None,
    ):
        if self._atomic is None:
            raise RuntimeError("Atomic Submission-Case repository is required")
        now = self._now()
        stage = action.removeprefix("case:")
        event = CaseEvent(
            event_id=self._event_id(submission, stage), case_id=case.case_id,
            event_type={
                "begin_submission": CaseEventType.SUBMITTING,
                "submit": CaseEventType.SUBMITTED,
                "acknowledge": CaseEventType.ACKNOWLEDGED,
            }[stage],
            occurred_at=now, actor_id=identity.principal.principal_id,
            source_channel=source_channel, source_ref=source_ref, notes=notes,
        )
        projection = deepcopy(case)
        method = {
            "begin_submission": projection.begin_submission,
            "submit": projection.submit,
            "acknowledge": projection.acknowledge,
        }[stage]
        kwargs = dict(
            event_id=event.event_id, occurred_at=now,
            actor_id=identity.principal.principal_id,
            source_channel=source_channel,
        )
        if stage == "acknowledge":
            kwargs.update(source_ref=source_ref, notes=notes)
        method(**kwargs)
        result = self._atomic.persist_mutation(
            submission=submission, expected_submission_version=expected_submission_version,
            case=projection, expected_case_version=expected_case_version,
            event=event, idempotency_key=event.event_id,
        )
        if not result.idempotent_replay:
            for name, value in projection.__dict__.items():
                setattr(case, name, deepcopy(value))
        return result

    def _acknowledge(
        self, *, case, submission, evidence_id, identity,
        source_channel, notes, execution_context=None,
    ):
        self._acknowledgement_evidence(case, evidence_id)
        now = self._now()
        updated = replace(
            submission, state="acknowledged", acknowledged_at=now,
            ack_ref=evidence_id, updated_at=now, version=submission.version + 1,
        )
        if self._atomic is not None:
            self._validate_execution_context(
                execution_context, identity,
                action="case:acknowledge", resource_id=case.case_id,
            )
            self._atomic_case_mutation(
                submission=updated, expected_submission_version=submission.version,
                case=case, expected_case_version=case.version,
                action="case:acknowledge", identity=identity,
                source_channel=source_channel, source_ref=evidence_id, notes=notes,
            )
            return
        self._save(updated, expected_version=submission.version)
        self._cases.transition(
            case.case_id, action="case:acknowledge", identity=identity,
            source_channel=source_channel, source_ref=evidence_id, notes=notes,
            execution_context=self._child_case_context(
                execution_context, identity, case.case_id, "case:acknowledge"
            ),
        )

    def _consequential_submission_decision(
        self, *, identity, case_id, consent_scope,
        explicit_user_approval, execution_context, idempotency_key,
    ):
        if execution_context is None:
            execution_context = CapabilityExecutionContext.for_capability(
                identity, capability_id=CAPABILITY_ID, action="case:submit",
                surface="shared", resource_id=case_id,
                side_effect_class="external_side_effect",
                idempotency_key=idempotency_key,
            )
        elif execution_context.idempotency_key != idempotency_key:
            raise ValueError("Execution idempotency key does not match the Submission idempotency key")
        requirement = ConsentRequirement(
            subject_id=identity.principal.principal_id,
            purpose=CONSENT_PURPOSE, scope=consent_scope,
        )
        request = ConsequentialOperationRequest(
            authorization=AuthorizationRequest(
                context=identity, capability=CAPABILITY_ID, action="case:submit",
                resource_id=case_id, requires_approval=True,
                execution_context=execution_context,
            ),
            execution_context=execution_context,
            consent_requirement=requirement,
            explicit_user_approval=explicit_user_approval,
        )
        if execution_context.identity.principal.principal_id != identity.principal.principal_id:
            raise PermissionError("Execution identity does not match the authenticated identity")
        require_execution_consent(
            self._consents, ExecutionConsentRequirement(requirement), execution_context
        )
        return gate_consequential_operation(
            request, consent_repository=self._consents
        )

    def submit(
        self, request: SubmissionRequest, *, identity: IdentityContext,
        explicit_user_approval: bool,
        execution_context: CapabilityExecutionContext | None = None,
    ) -> CivicCaseResult:
        return CivicCaseResult(
            submit_request(
                self, request, identity=identity,
                explicit_user_approval=explicit_user_approval,
                execution_context=execution_context,
            ),
            AuthorizationDecision.ALLOW,
        )

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

    @staticmethod
    def _validate_execution_context(execution_context, identity, *, action, resource_id=None):
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
    def _child_case_context(parent, identity, case_id, action):
        if parent is None:
            return None
        return CapabilityExecutionContext.for_capability(
            identity, capability_id="JNV-CIVIC-COMPLAINT", action=action,
            surface=parent.surface, resource_id=case_id,
            correlation_id=parent.correlation_id,
            parent_operation_id=parent.operation_id,
            authorization_ref=parent.authorization_ref,
            consent_refs=parent.consent_refs, policy_ref=parent.policy_ref,
            risk_level=parent.risk_level,
            side_effect_class=parent.side_effect_class,
            provenance=parent.provenance, metadata=parent.metadata,
        )
