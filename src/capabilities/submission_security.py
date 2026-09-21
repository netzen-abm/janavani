"""Authorization and execution-context gates for submission."""
from __future__ import annotations

from src.access.authorization import AuthorizationRequest
from src.access.consequential import (
    ConsequentialOperationRequest, gate_consequential_operation,
)
from src.access.consent import ConsentRequirement
from src.access.execution_consent import (
    ExecutionConsentRequirement, require_execution_consent,
)
from src.core.execution import CapabilityExecutionContext

CAPABILITY_ID = "case:submit"
CONSENT_PURPOSE = "case_submission"


class SubmissionSecurity:
    def __init__(self, capability):
        self.c = capability

    def decision(
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
                context=identity, capability=CAPABILITY_ID,
                action="case:submit", resource_id=case_id,
                requires_approval=True, execution_context=execution_context,
            ),
            execution_context=execution_context,
            consent_requirement=requirement,
            explicit_user_approval=explicit_user_approval,
        )
        self.validate(execution_context, identity, action="case:submit", resource_id=case_id)
        require_execution_consent(
            self.c._consents, ExecutionConsentRequirement(requirement),
            execution_context,
        )
        return gate_consequential_operation(
            request, consent_repository=self.c._consents
        )

    @staticmethod
    def validate(execution_context, identity, *, action, resource_id=None):
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
    def child_context(parent, identity, case_id, action):
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
