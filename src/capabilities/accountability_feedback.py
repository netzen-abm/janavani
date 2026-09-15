"""Canonical, provider- and surface-neutral accountability feedback capability."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.core.accountability_feedback import AccountabilityFeedback, AccountabilityFeedbackRepository
from src.utils.feedback_validators import ContentSanitizationEngine


class AccountabilityFeedbackCapability:
    """Validate and persist citizen feedback without owning transport or UI."""

    def __init__(self, repository: AccountabilityFeedbackRepository):
        self._repository = repository

    def submit(
        self,
        *,
        office_id: str,
        rating: int,
        issue: str,
        actor_ref: str | None = None,
        source_channel: str | None = None,
    ) -> AccountabilityFeedback:
        office = str(office_id).strip()
        if not office:
            raise ValueError("office_id is required")
        try:
            rating_value = int(rating)
        except (TypeError, ValueError) as exc:
            raise ValueError("Rating must be an integer between 1 and 5") from exc
        if not 1 <= rating_value <= 5:
            raise ValueError("Rating must be between 1 and 5")

        narrative = ContentSanitizationEngine.sanitize_commentary(str(issue))
        if not narrative:
            raise ValueError("Feedback issue is required")
        if not ContentSanitizationEngine.is_safe(narrative):
            raise ValueError("Feedback contains disallowed content")

        feedback = AccountabilityFeedback(
            feedback_id=f"FB-{uuid4().hex}",
            office_id=office,
            rating=rating_value,
            issue=narrative,
            submitted_at=datetime.now(timezone.utc).isoformat(),
            actor_ref=actor_ref,
            source_channel=source_channel,
        )
        return self._repository.save(feedback)
