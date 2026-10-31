"""Telegram identity adapter.

A Telegram identifier is a provider subject, never a canonical citizen ID.
Persistent capability access requires an explicit verified identity link.
"""
from __future__ import annotations

from src.identity.linking import (
    ExternalIdentityLinkRepository,
    context_for_verified_external_link,
)


def identity_for_telegram_user(
    user_id: int,
    *,
    links: ExternalIdentityLinkRepository | None = None,
):
    if user_id <= 0:
        raise ValueError("Telegram user identity is required")
    if links is None:
        raise PermissionError("Telegram identity must be explicitly linked before protected access")
    # This is authentication mapping only; the shared authorization boundary
    # determines the capabilities/actions this canonical principal can use.
    return context_for_verified_external_link(
        links,
        provider="telegram",
        subject=str(user_id),
    )
