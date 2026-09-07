"""Web adapter for the shared Civic Case capability.

HTTP concerns stay here; case creation semantics live in src.capabilities.
"""
from __future__ import annotations

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository


def create_case_capability(
    repository: CivicCaseRepository,
    *,
    identity: IdentityContext,
    case_type: CaseType,
    subject: str,
    narrative: str,
    source_channel: str = "webapp",
) -> CivicCase:
    """Create a case through the shared capability and return the canonical case."""
    result = CivicCaseCapability(repository).create(
        CivicCaseCreateRequest(case_type=case_type, subject=subject, narrative=narrative),
        identity=identity,
        source_channel=source_channel,
    )
    return result.case
