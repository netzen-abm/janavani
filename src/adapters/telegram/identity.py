"""Telegram identity adapter.

A Telegram identifier is a provider subject, never a canonical citizen ID.
Persistent capability access requires an explicit verified identity link.
"""
from __future__ import annotations

from dataclasses import replace

from src.adapters.telegram.identity import __name__ as _identity_module_name
from src.capabilities.civic_case import CAPABILITY_ID
from src.identity.adapter import DefaultIdentityAdapter
from src.identity.context import IdentityContext
from src.identity.linking import ExternalIdentityLinkRepository, IdentityLinkResolver


def identity_for_telegram_user(
    user_id: int,
    *,
    links: ExternalIdentityLinkRepository | None = None,
) -> IdentityContext:
    if user_id <= 0:
        raise ValueError("Telegram user identity is required")
    if links is None:
        raise PermissionError("Telegram identity must be explicitly linked before protected access")
    external = IdentityLinkResolver(links).resolve("telegram", str(user_id))
    context = DefaultIdentityAdapter().resolve(external)

    # An explicitly verified citizen link receives only the baseline self-service
    # Case-creation capability. This adapter does not grant administrative,
    # submission, or other consequential capabilities.
    principal = replace(
        context.principal,
        capabilities=context.principal.capabilities | frozenset({CAPABILITY_ID}),
    )
    return IdentityContext(principal=principal, request_id=context.request_id)
