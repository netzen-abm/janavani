"""Provider-neutral reconciliation of ambiguous submission outcomes."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.core.civic_case import CaseStatus
from src.core.execution import CapabilityExecutionContext
from src.core.submission import SubmissionRecord, SubmissionRepository
from src.core.submission_recovery import reconcile_unknown_submission
from src.identity.context import IdentityContext

CAPABILITY_ID = "case:submit"
RECONCILE_ACTION = "case:reconcile_submission"


@dataclass(frozen=True)
class SubmissionReconciliationObservation:
    """Trusted provider-neutral observation of an external submission."""

    outcome: str
    observed_at: str
    source_ref: str
    external_reference: str | None = None

    def __post_init__(self) -> None:
        if self.outcome not in {"submitted", "failed"}:
            raise ValueError("Reconciliation outcome must be submitted or failed")
        if not self.observed_at.strip():
            raise ValueError("observed_at is required")
        if not self.source_ref.strip():
            raise ValueError("source_ref is required")


class SubmissionReconciliationSource(Protocol):
    """Independent observation source; provider adapters implement this boundary."""

    def reconcile(self, submission: SubmissionRecord) -> SubmissionReconciliationObservation: ...


class SubmissionReconciliationCapability:
    """Authorize and persist an independently observed unknown outcome."""

    def __init__(self, case_capability: CivicCaseCapability,
                 submission_repository: SubmissionRepository,
                 observation_source: SubmissionReconciliationSource) -> None:
        self._cases = case_capability
        self._submissions = submission_repository
        self._source = observation_source

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def reconcile(self, submission_id: str, *, identity: IdentityContext,
                  execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, submission_id)
        decision = authorize(AuthorizationRequest(
            context=identity,
            capability=CAPABILITY_ID,
            action=RECONCILE_ACTION,
            resource_id=submission_id,
        ))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to reconcile this submission")

        submission = self._submissions.get(submission_id)
        if submission is None:
            raise LookupError("Submission not found")
        if submission.state != "unknown":
            raise ValueError("Only an unknown submission can be reconciled")

        observation = self._source.reconcile(submission)
        updated = reconcile_unknown_submission(
            submission,
            outcome=observation.outcome,
            reconciled_at=observation.observed_at,
            external_reference=observation.external_reference,
        )
        self._submissions.update_if_version(updated, expected_version=submission.version)

        case = self._cases.get_owned(submission.case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if updated.state == "submitted":
            if case.status in {CaseStatus.SUBMITTING, CaseStatus.QUEUED}:
                case_context = self._child_case_context(execution_context, identity, case.case_id)
                self._cases.transition(
                    case.case_id,
                    action="case:submit",
                    identity=identity,
                    source_channel=submission.channel,
                    source_ref=observation.source_ref,
                    notes="Submission outcome reconciled from an independent observation",
                    execution_context=case_context,
                )
            elif case.status is not CaseStatus.SUBMITTED:
                raise ValueError(f"Case is not in a reconcilable submission state: {case.status.value}")

        final_case = self._cases.get_owned(case.case_id, identity=identity)
        if final_case is None:
            raise LookupError("Case not found after reconciliation")
        return CivicCaseResult(final_case, AuthorizationDecision.ALLOW)

    @staticmethod
    def _validate_execution_context(execution_context: CapabilityExecutionContext | None,
                                    identity: IdentityContext, submission_id: str) -> None:
        if execution_context is None:
            return
        if execution_context.identity.principal.principal_id != identity.principal.principal_id:
            raise PermissionError("Execution identity does not match the authenticated identity")
        if execution_context.capability_id != CAPABILITY_ID:
            raise ValueError("Execution capability does not match the Submission capability")
        if execution_context.action != RECONCILE_ACTION:
            raise ValueError("Execution action does not match submission reconciliation")
        if execution_context.resource_id != submission_id:
            raise ValueError("Execution resource does not match the submission")

    @staticmethod
    def _child_case_context(parent: CapabilityExecutionContext | None,
                            identity: IdentityContext, case_id: str) -> CapabilityExecutionContext | None:
        if parent is None:
            return None
        return CapabilityExecutionContext.for_capability(
            identity,
            capability_id="JNV-CIVIC-COMPLAINT",
            action="case:submit",
            surface=parent.surface,
            resource_id=case_id,
            correlation_id=parent.correlation_id,
            parent_operation_id=parent.operation_id,
            authorization_ref=parent.authorization_ref,
            consent_refs=parent.consent_refs,
            policy_ref=parent.policy_ref,
            risk_level=parent.risk_level,
            side_effect_class=parent.side_effect_class,
            provenance=parent.provenance,
            metadata=parent.metadata,
        )
