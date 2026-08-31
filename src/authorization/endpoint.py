"""Execution-boundary authorization helpers."""

from src.identity.context import IdentityContext

from .policy import AuthorizationPolicy


class AuthorizationDenied(PermissionError):
    """Raised when a caller is not permitted to execute a capability."""


def authorize_capability(
    context: IdentityContext,
    capability: str,
    *,
    policy: AuthorizationPolicy,
) -> None:
    """Enforce capability authorization at the action boundary."""
    if not capability or not policy.permits(context, capability):
        raise AuthorizationDenied(f"capability denied: {capability}")
