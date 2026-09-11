"""Provider-neutral gate for consequential capability operations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.access.authorization import AuthorizationDecision, AuthorizationPolicy, AuthorizationRequest
from src.access.consent import ConsentRepositoryReader, ConsentRequiredError, ConsentRequirement, require_consent
from src.core.execution import CapabilityExecutionContext, SideEffectClass


class ConsequentialDecision(str, Enum):
    """Deterministic outcome of the composed consequential-operation gate."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    CONSENT_REQUIRED = "consent_required"


@dataclass(frozen=True)
class ConsequentialOperationRequest:
    """Inputs required before a consequential capability operation may execute."""

    authorization: AuthorizationRequest
    execution_context: CapabilityExecutionContext
    consent_requirement: ConsentRequirement | None = None
    explicit_user_approval: bool = False


class ConsequentialOperationGate:
    """Compose identity, authorization, consent, and approval without collapsing them."""

    def __init__(self, authorization_policy: AuthorizationPolicy | None = None) -> None:
        self._authorization_policy = authorization_policy or AuthorizationPolicy()

    def evaluate(
        self,
        request: ConsequentialOperationRequest,
        *,
        consent_repository: ConsentRepositoryReader | None = None,
    ) -> ConsequentialDecision:
        """Fail closed unless every required control permits the operation."""
        authorization = self._authorization_policy.evaluate(
            AuthorizationRequest(
                context=request.authorization.context,
                capability=request.authorization.capability,
                action=request.authorization.action,
                resource_id=request.authorization.resource_id,
                risk_level=request.authorization.risk_level,
                requires_approval=request.authorization.requires_approval,
                execution_context=request.execution_context,
            )
        )

        if authorization is AuthorizationDecision.DENY:
            return ConsequentialDecision.DENY

        if request.consent_requirement is not None:
            if consent_repository is None:
                return ConsequentialDecision.CONSENT_REQUIRED
            try:
                require_consent(consent_repository, request.consent_requirement)
            except ConsentRequiredError:
                return ConsequentialDecision.CONSENT_REQUIRED

        approval_required = (
            authorization is AuthorizationDecision.REQUIRE_APPROVAL
            or request.authorization.requires_approval
            or request.execution_context.side_effect_class
            is SideEffectClass.EXTERNAL_SIDE_EFFECT
            and request.authorization.risk_level in {"high", "critical"}
        )
        if approval_required and not request.explicit_user_approval:
            return ConsequentialDecision.REQUIRE_APPROVAL

        return ConsequentialDecision.ALLOW


def gate_consequential_operation(
    request: ConsequentialOperationRequest,
    *,
    consent_repository: ConsentRepositoryReader | None = None,
    authorization_policy: AuthorizationPolicy | None = None,
) -> ConsequentialDecision:
    """Evaluate a consequential operation using the shared gate."""
    return ConsequentialOperationGate(authorization_policy).evaluate(
        request,
        consent_repository=consent_repository,
    )
