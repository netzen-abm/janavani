"""Telegram adapter over the canonical shared surface composition."""
from __future__ import annotations

from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.capabilities.civic_case import CivicCaseCreateRequest
from src.platform.surface_case_composition import create_surface_case_composition
from src.storage.repositories.civic_case import CivicCaseRepository


def create_case_from_telegram(
    repository: CivicCaseRepository,
    *,
    identity: IdentityContext,
    subject: str,
    narrative: str,
) -> CivicCase:
    """Create a Telegram-originated case through shared infrastructure."""
    composition = create_surface_case_composition()
    return composition.case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject=subject,
            narrative=narrative,
        ),
        identity=identity,
        source_channel="telegram",
    ).case
