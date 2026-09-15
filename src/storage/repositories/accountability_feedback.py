"""Development/test repository for canonical accountability feedback."""
from __future__ import annotations

from src.core.accountability_feedback import AccountabilityFeedback


class InMemoryAccountabilityFeedbackRepository:
    """Provider-neutral repository implementation for local composition and tests."""

    def __init__(self):
        self._records: dict[str, AccountabilityFeedback] = {}

    def save(self, feedback: AccountabilityFeedback) -> AccountabilityFeedback:
        if feedback.feedback_id in self._records:
            raise ValueError(f"Feedback already exists: {feedback.feedback_id}")
        self._records[feedback.feedback_id] = feedback
        return feedback

    def get(self, feedback_id: str) -> AccountabilityFeedback | None:
        return self._records.get(feedback_id)

    def list_for_office(self, office_id: str) -> list[AccountabilityFeedback]:
        return [record for record in self._records.values() if record.office_id == office_id]
