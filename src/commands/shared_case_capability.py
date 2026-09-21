"""Telegram adapter over the canonical shared surface composition."""
from __future__ import annotations

from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.capabilities.civic_case import CivicCaseCreateRequest
from src.capabilities.civic_case_impl import CivicCaseCapability
from src.storage.repositories.civic_case import CivicCaseRepository


def create_case_from_telegram(
    repository: CivicCaseRepository,
    *,
    identity: IdentityContext,
    subject: str,
    narrative: str,
    case_capability: CivicCaseCapability | None = None,
) -> CivicCase:
    """Create a Telegram-originated case through shared infrastructure."""
    # The Telegram application passes the canonical composed capability. The
    # repository remains a compatibility seam for isolated tests/legacy callers;
    # it is used only when no composed capability is supplied.
    capability = case_capability or CivicCaseCapability(repository)
    return capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject=subject,
            narrative=narrative,
        ),
        identity=identity,
        source_channel="telegram",
    ).case
