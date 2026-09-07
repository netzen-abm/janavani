"""Telegram adapter for the shared Civic Case capability."""
from __future__ import annotations

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository


def create_case_from_telegram(
    repository: CivicCaseRepository,
    *,
    identity: IdentityContext,
    subject: str,
    narrative: str,
) -> CivicCase:
    """Create a Telegram-originated case through the canonical capability."""
    return CivicCaseCapability(repository).create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject=subject,
            narrative=narrative,
        ),
        identity=identity,
        source_channel="telegram",
    ).case
