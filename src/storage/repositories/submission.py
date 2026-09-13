"""Provider-neutral in-memory submission repository."""
from __future__ import annotations

from src.core.submission import RECOVERABLE_SUBMISSION_STATE, SubmissionRecord, SubmissionRepository


class SubmissionConcurrencyError(RuntimeError):
    """The caller attempted to mutate a newer submission version."""


class SubmissionIdempotencyConflictError(RuntimeError):
    """An idempotency key was reused for a different submission payload."""


def _same_operation(left: SubmissionRecord, right: SubmissionRecord) -> bool:
    return (
        left.case_id == right.case_id
        and left.destination_ref == right.destination_ref
        and left.document_ref == right.document_ref
        and left.channel == right.channel
    )


class InMemorySubmissionRepository(SubmissionRepository):
    """Reference implementation for tests and local development."""

    def __init__(self) -> None:
        self._items: dict[str, SubmissionRecord] = {}

    def save(self, submission: SubmissionRecord) -> None:
        self._items[submission.submission_id] = submission

    def get(self, submission_id: str) -> SubmissionRecord | None:
        return self._items.get(submission_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> SubmissionRecord | None:
        return next((item for item in self._items.values() if item.idempotency_key == idempotency_key), None)

    def create_idempotent(self, submission: SubmissionRecord) -> tuple[SubmissionRecord, bool]:
        if not submission.idempotency_key:
            raise ValueError("idempotency_key is required")
        existing = self.get_by_idempotency_key(submission.idempotency_key)
        if existing is not None:
            if not _same_operation(existing, submission):
                raise SubmissionIdempotencyConflictError(
                    "Idempotency key is already bound to a different submission operation"
                )
            return existing, True
        if submission.submission_id in self._items:
            raise SubmissionIdempotencyConflictError("submission_id is already bound to another record")
        self._items[submission.submission_id] = submission
        return submission, False

    def update_if_version(self, submission: SubmissionRecord, *, expected_version: int) -> None:
        current = self._items.get(submission.submission_id)
        if current is None:
            raise LookupError("Submission not found")
        if current.version != expected_version:
            raise SubmissionConcurrencyError(
                f"Submission version mismatch: expected {expected_version}, found {current.version}"
            )
        if submission.version != expected_version + 1:
            raise ValueError("Submission mutation must increment version by exactly one")
        if submission.idempotency_key != current.idempotency_key:
            raise ValueError("Submission idempotency key is immutable")
        self._items[submission.submission_id] = submission

    def list_for_case(self, case_id: str) -> tuple[SubmissionRecord, ...]:
        return tuple(item for item in self._items.values() if item.case_id == case_id)

    def list_recoverable(self) -> tuple[SubmissionRecord, ...]:
        return tuple(
            item for item in self._items.values()
            if item.state == RECOVERABLE_SUBMISSION_STATE
        )
