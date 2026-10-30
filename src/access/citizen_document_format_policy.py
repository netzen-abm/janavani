"""Authorization policy for citizen-owned reusable document structures."""
from __future__ import annotations

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.identity.context import IdentityContext

FORMAT_CAPABILITY = "document:format:manage"


def require_format_permission(context: IdentityContext, action: str, *, format_id: str | None = None) -> None:
    """Deny anonymous and unscoped principals before any repository access."""
    decision = authorize(
        AuthorizationRequest(
            context=context,
            capability=FORMAT_CAPABILITY,
            action=action,
            resource_id=format_id,
            resource_owner_id=context.principal.principal_id,
        )
    )
    if decision is not AuthorizationDecision.ALLOW:
        raise PermissionError("This account is not permitted to manage saved document formats")
