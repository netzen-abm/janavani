"""Provider-neutral accountability feedback contracts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AccountabilityFeedback:
    """Canonical citizen feedback record for public-service experience."""

    feedback_id: str
    office_id: str
    rating: int
    issue: str
    submitted_at: str
    department_name: str | None = None
    actor_ref: str | None = None
    source_channel: str | None = None


class AccountabilityFeedbackRepository(Protocol):
    """Persistence contract owned by the capability, not an access surface."""

    def save(self, feedback: AccountabilityFeedback) -> AccountabilityFeedback:
        """Persist one canonical feedback record."""

    def get(self, feedback_id: str) -> AccountabilityFeedback | None:
        """Return one feedback record when present."""

    def list_for_office(self, office_id: str) -> list[AccountabilityFeedback]:
        """Return feedback records associated with an office."""
