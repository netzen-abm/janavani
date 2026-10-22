"""Least-privilege capabilities for a Telegram identity after explicit verification.

Identity links prove which citizen a Telegram subject belongs to. They do not
store or confer arbitrary permissions. This policy gives a verified linked
citizen only the baseline capabilities required for their own civic Case flow;
administrative, service, destination, delivery and unrelated capabilities are
never inherited through Telegram identity pairing.
"""
from __future__ import annotations

from src.capabilities.civic_case_contract import CAPABILITY_ID
from src.identity.external import ExternalIdentity

TELEGRAM_CITIZEN_CAPABILITIES = frozenset({
    CAPABILITY_ID,
    "case:read",
    "case:write",
    "case:review",
    "case:evidence",
    "evidence:register",
    "evidence:read",
    "document:review",
})


def capabilities_for_verified_telegram_citizen(identity: ExternalIdentity) -> frozenset[str]:
    """Return the fixed baseline citizen grants for a usable Telegram identity link."""
    if identity.provider != "telegram":
        raise PermissionError("Telegram citizen policy requires a Telegram identity")
    if not identity.is_usable():
        raise PermissionError("An active, verified Telegram identity link is required")
    return TELEGRAM_CITIZEN_CAPABILITIES
