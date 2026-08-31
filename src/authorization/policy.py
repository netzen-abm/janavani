"""Capability authorization policy.

Authorization is evaluated after adapter identity resolution and before
capability execution. Authentication, authorization, and consent remain
separate concerns.
"""

from dataclasses import dataclass
from typing import FrozenSet

from src.identity.context import IdentityContext


@dataclass(frozen=True)
class AuthorizationDecision:
    """Immutable result of an authorization evaluation."""

    allowed: bool
    reason: str
    capability: str


class AuthorizationPolicy:
    """Minimal deny-by-default policy for shared capability execution."""

    def __init__(self, anonymous_capabilities: FrozenSet[str] = frozenset()):
        self._anonymous_capabilities = anonymous_capabilities

    def authorize(self, context: IdentityContext, capability: str) -> AuthorizationDecision:
        """Authorize a capability for the normalized request context."""
        principal = context.principal

        if capability in self._anonymous_capabilities:
            return AuthorizationDecision(True, "capability permits anonymous access", capability)

        if principal.has_capability(capability):
            return AuthorizationDecision(True, "principal has capability", capability)

        return AuthorizationDecision(False, "capability not granted", capability)
