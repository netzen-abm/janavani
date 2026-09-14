"""Provider-neutral atomic Submission + Civic Case persistence boundary.

This module contains only the transaction contract and result types. Concrete
providers may implement the boundary without leaking provider types into the
capability layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.civic_case import CaseEvent, CivicCase
from src.core.submission import SubmissionRecord


class SubmissionCaseTransactionError(RuntimeError):
    """Base error for atomic Submission + Case persistence."""


class SubmissionCaseConcurrencyError(SubmissionCaseTransactionError):
    """Either the Submission or Case version is stale."""


class SubmissionCaseIdempotencyConflictError(SubmissionCaseTransactionError):
    """The durable operation key was reused with a different mutation."""


@dataclass(frozen=True)
class SubmissionCaseMutationResult:
    """Committed versions for one atomic local mutation."""

    submission_id: str
    submission_version: int
    case_id: str
    case_version: int
    event_id: str
    idempotent_replay: bool = False


class SubmissionCaseTransactionRepository(Protocol):
    """Atomic local persistence for coupled Submission and Case mutations.

    The boundary intentionally excludes external transport. A provider must
    commit the Submission mutation, Case projection and lifecycle event in one
    transaction or commit none of them.
    """

    def persist_mutation(
        self,
        *,
        submission: SubmissionRecord,
        expected_submission_version: int,
        case: CivicCase,
        expected_case_version: int,
        event: CaseEvent,
        idempotency_key: str,
    ) -> SubmissionCaseMutationResult: ...
