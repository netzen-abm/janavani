"""Capability authorization policy.

Authorization is evaluated after adapter identity resolution and before
capability execution. Authentication, authorization, and consent remain
separate concerns.
"""

from dataclasses import dataclass
from typing import FrozenSet

from src.identity.context import IdentityContext
from .capabilities import PUBLIC_CAPABILITIES, PROTECTED_CAPABILITIES


@dataclass(frozen=True)
class AuthorizationDecision:
    """Immutable result of an authorization evaluation."""

    allowed: bool
    reason: str
    capability: str


class AuthorizationPolicy:
    """Deny-by-default policy with a canonical capability registry."""

    def __init__(self, anonymous_capabilities: FrozenSet[str] | None = None):
        # A caller may further restrict anonymous access, but may not expand it
        # beyond the centrally defined public capability set.
        requested = PUBLIC_CAPABILITIES if anonymous_capabilities is None else anonymous_capabilities
        self._anonymous_capabilities = frozenset(requested) & PUBLIC_CAPABILITIES

    def authorize(self, context: IdentityContext, capability: str) -> AuthorizationDecision:
        """Authorize a capability for the normalized request context."""
        principal = context.principal

        if capability not in PUBLIC_CAPABILITIES and capability not in PROTECTED_CAPABILITIES:
            return AuthorizationDecision(False, "unknown capability denied", capability)

        if capability in self._anonymous_capabilities:
            return AuthorizationDecision(True, "capability permits anonymous access", capability)

        if principal.has_capability(capability):
            return AuthorizationDecision(True, "principal has capability", capability)

        return AuthorizationDecision(False, "capability not granted", capability)
