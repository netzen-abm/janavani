from dataclasses import replace

import pytest

from src.core.submission import (
    SubmissionConcurrencyError,
    SubmissionIdempotencyConflictError,
    SubmissionRecord,
)
from src.storage.repositories.submission import InMemorySubmissionRepository


def make_submission(*, key: str = "idem-1", submission_id: str = "sub-1") -> SubmissionRecord:
    return SubmissionRecord.new(
        submission_id=submission_id,
        case_id="case-1",
        destination_ref="office-1",
        document_ref="doc-1",
        channel="web",
        idempotency_key=key,
    )


def test_same_idempotency_key_same_operation_is_replay() -> None:
    repository = InMemorySubmissionRepository()
    first, replay = repository.create_idempotent(make_submission())
    second, replay_again = repository.create_idempotent(make_submission(submission_id="sub-2"))

    assert replay is False
    assert replay_again is True
    assert second.submission_id == first.submission_id
    assert len(repository.list_for_case("case-1")) == 1


def test_same_idempotency_key_different_operation_is_conflict() -> None:
    repository = InMemorySubmissionRepository()
    repository.create_idempotent(make_submission())
    conflicting = replace(make_submission(), destination_ref="office-2", submission_id="sub-2")

    with pytest.raises(SubmissionIdempotencyConflictError):
        repository.create_idempotent(conflicting)


def test_stale_version_is_rejected() -> None:
    repository = InMemorySubmissionRepository()
    original, _ = repository.create_idempotent(make_submission())
    current = replace(original, state="submitting", version=2)
    repository.update_if_version(current, expected_version=1)

    stale = replace(current, state="failed", version=2)
    with pytest.raises(SubmissionConcurrencyError):
        repository.update_if_version(stale, expected_version=1)


def test_idempotency_key_is_stable_across_state_mutations() -> None:
    repository = InMemorySubmissionRepository()
    original, _ = repository.create_idempotent(make_submission())
    current = replace(original, state="submitting", version=2)
    repository.update_if_version(current, expected_version=1)

    assert repository.get_by_idempotency_key("idem-1") == current
