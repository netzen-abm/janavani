"""Shared consent enforcement for consequential Janavani capability actions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.consent import Consent, ConsentStatus


class ConsentRepositoryReader(Protocol):
    """Minimal repository contract required by consent enforcement."""

    def list_for_subject(self, subject_id: str) -> list[Consent]:
        ...


class ConsentRequiredError(PermissionError):
    """Raised when an action requires valid consent that is not available."""


@dataclass(frozen=True)
class ConsentRequirement:
    """Consent required for a capability purpose and scope."""

    subject_id: str
    purpose: str
    scope: str


def require_consent(
    repository: ConsentRepositoryReader,
    requirement: ConsentRequirement,
) -> None:
    """Fail closed unless a granted consent authorizes the requested operation."""
    consents = repository.list_for_subject(requirement.subject_id)
    for consent in consents:
        if consent.status is not ConsentStatus.GRANTED:
            continue
        if consent.authorizes(requirement.purpose, requirement.scope):
            return
    raise ConsentRequiredError(
        "Explicit consent is required for this capability operation"
    )
