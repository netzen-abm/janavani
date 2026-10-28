"""Request-scoped policy for explicitly opted-in remote civic drafting.

The policy grants no persistent account permission. It derives a temporary
execution identity only after the surface has authenticated the caller and the
caller has explicitly consented to remote AI processing.
"""
from __future__ import annotations

from dataclasses import replace

from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode

CIVIC_DRAFT_AI_CAPABILITY = "civic:ai-draft"


def identity_for_explicit_remote_drafting(
    identity: IdentityContext | None,
    *,
    explicit_consent: bool,
) -> IdentityContext:
    """Return a request-scoped AI capability for an authenticated consenting citizen."""
    if not explicit_consent:
        raise PermissionError("Explicit consent for remote AI drafting is required")
    if identity is None:
        raise PermissionError("An authenticated identity is required for remote AI drafting")

    principal = identity.principal
    if principal.identity_mode is not IdentityMode.AUTHENTICATED:
        raise PermissionError("Remote AI drafting requires an authenticated identity")
    if principal.authentication_method is AuthenticationMethod.NONE:
        raise PermissionError("Remote AI drafting requires a verified authentication method")
    if not principal.principal_id.strip():
        raise PermissionError("A canonical citizen principal is required")

    # This is a one-request opt-in. Never persist this derived capability to the
    # user's link, account, profile, session or future requests.
    granted = frozenset((*principal.capabilities, CIVIC_DRAFT_AI_CAPABILITY))
    return replace(identity, principal=replace(principal, capabilities=granted))
