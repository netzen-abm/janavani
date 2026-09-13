"""Provider-neutral in-memory submission repository."""
from __future__ import annotations

from src.core.submission import RECOVERABLE_SUBMISSION_STATE, SubmissionRecord, SubmissionRepository


class InMemorySubmissionRepository(SubmissionRepository):
    """Reference implementation for tests and local development."""

    def __init__(self) -> None:
        self._items: dict[str, SubmissionRecord] = {}

    def save(self, submission: SubmissionRecord) -> None:
        self._items[submission.submission_id] = submission

    def get(self, submission_id: str) -> SubmissionRecord | None:
        return self._items.get(submission_id)

    def list_for_case(self, case_id: str) -> tuple[SubmissionRecord, ...]:
        return tuple(
            item for item in self._items.values() if item.case_id == case_id
        )

    def list_recoverable(self) -> tuple[SubmissionRecord, ...]:
        return tuple(
            item for item in self._items.values()
            if item.state == RECOVERABLE_SUBMISSION_STATE
        )
