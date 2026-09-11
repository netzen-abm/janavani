"""Provider-neutral authorization kernel for Janavani capabilities."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext


class AuthorizationDecision(str, Enum):
    """Deterministic outcome of an authorization evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class AuthorizationRequest:
    """Inputs required for a capability-level authorization decision."""

    context: IdentityContext
    capability: str
    action: str
    resource_id: Optional[str] = None
    resource_owner_id: Optional[str] = None
    risk_level: str = "normal"
    requires_approval: bool = False
    execution_context: CapabilityExecutionContext | None = None


class AuthorizationPolicy:
    """Canonical policy decision boundary with resource and execution consistency checks."""

    def evaluate(self, request: AuthorizationRequest) -> AuthorizationDecision:
        principal = request.context.principal

        if not request.capability or not request.action:
            return AuthorizationDecision.DENY

        if request.resource_owner_id is not None and request.resource_owner_id != principal.principal_id:
            return AuthorizationDecision.DENY

        if request.execution_context is not None:
            envelope = request.execution_context
            if envelope.identity.principal.principal_id != principal.principal_id:
                return AuthorizationDecision.DENY
            if envelope.capability_id != request.capability:
                return AuthorizationDecision.DENY
            if envelope.action != request.action:
                return AuthorizationDecision.DENY
            if request.resource_id is not None and envelope.resource_id != request.resource_id:
                return AuthorizationDecision.DENY
            if envelope.risk_level != request.risk_level:
                return AuthorizationDecision.DENY
            if request.requires_approval and envelope.side_effect_class is SideEffectClass.READ:
                return AuthorizationDecision.DENY

        if not principal.has_capability(request.capability):
            return AuthorizationDecision.DENY

        if request.risk_level == "high" or request.requires_approval:
            return AuthorizationDecision.REQUIRE_APPROVAL

        return AuthorizationDecision.ALLOW


def authorize(request: AuthorizationRequest) -> AuthorizationDecision:
    """Evaluate a request using the canonical shared authorization policy."""
    return AuthorizationPolicy().evaluate(request)
