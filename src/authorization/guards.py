"""Reusable enforcement helpers for capability entry points."""

from .policy import AuthorizationPolicy
from src.identity.context import IdentityContext


class AuthorizationDenied(PermissionError):
    """Raised when a request cannot execute a capability."""


def require_capability(
    context: IdentityContext,
    capability: str,
    *,
    policy: AuthorizationPolicy | None = None,
) -> None:
    """Fail closed unless the shared policy explicitly permits execution."""
    decision = (policy or AuthorizationPolicy()).authorize(context, capability)
    if not decision.allowed:
        raise AuthorizationDenied(decision.reason)
