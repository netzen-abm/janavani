"""Provider-neutral authorization kernel for Janavani capabilities."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

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
    risk_level: str = "normal"
    requires_approval: bool = False


class AuthorizationPolicy:
    """Minimal shared authorization policy with explicit least privilege."""

    def evaluate(self, request: AuthorizationRequest) -> AuthorizationDecision:
        principal = request.context.principal

        if not request.capability or not request.action:
            return AuthorizationDecision.DENY

        if not principal.has_capability(request.capability):
            return AuthorizationDecision.DENY

        if request.risk_level == "high" or request.requires_approval:
            return AuthorizationDecision.REQUIRE_APPROVAL

        return AuthorizationDecision.ALLOW


def authorize(request: AuthorizationRequest) -> AuthorizationDecision:
    """Evaluate a request using the canonical shared authorization policy."""
    return AuthorizationPolicy().evaluate(request)
