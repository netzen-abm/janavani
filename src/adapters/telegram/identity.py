"""Telegram identity adapter.

A Telegram identifier is a provider subject, never a canonical citizen ID.
Persistent capability access requires an explicit verified identity link.
"""
from __future__ import annotations

from dataclasses import replace

from src.access.telegram_citizen_capability_policy import (
    capabilities_for_verified_telegram_citizen,
)
from src.identity.adapter import DefaultIdentityAdapter
from src.identity.context import IdentityContext
from src.identity.external import ExternalIdentity
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
    # An identity link proves ownership, not arbitrary permission. Resolve only
    # the fixed baseline citizen grants at the canonical authorization boundary.
    external = replace(
        external,
        capabilities=capabilities_for_verified_telegram_citizen(external),
    )
    return DefaultIdentityAdapter().resolve(external)
