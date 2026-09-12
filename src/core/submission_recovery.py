"""Restart-safe submission recovery semantics.

A process interruption after an external send begins can leave the local
system unable to know whether the destination accepted the submission. This
module makes that uncertainty explicit: ``submitting`` becomes ``unknown``
until an independent reconciliation establishes an outcome.
"""
from __future__ import annotations

from dataclasses import replace
from enum import Enum

from src.core.submission import SubmissionRecord


class SubmissionState(str, Enum):
    CREATED = "created"
    SUBMITTING = "submitting"
    UNKNOWN = "unknown"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


class SubmissionRecoveryError(RuntimeError):
    """Invalid recovery transition or unsafe retry attempt."""


def mark_interrupted_submission_unknown(
    submission: SubmissionRecord,
    *,
    recovered_at: str,
) -> SubmissionRecord:
    """Convert an interrupted in-flight submission to explicit uncertainty.

    This operation never claims success and never increments the retry count:
    no new external delivery attempt has occurred.
    """
    if submission.state != SubmissionState.SUBMITTING.value:
        raise SubmissionRecoveryError(
            "Only an in-flight submission can be recovered as unknown"
        )
    return replace(
        submission,
        state=SubmissionState.UNKNOWN.value,
        error_code="unknown_outcome_after_restart",
        updated_at=recovered_at,
        version=submission.version + 1,
    )


def reconcile_unknown_submission(
    submission: SubmissionRecord,
    *,
    outcome: str,
    reconciled_at: str,
    external_reference: str | None = None,
) -> SubmissionRecord:
    """Record an externally verified outcome for an unknown submission.

    ``outcome`` must be ``submitted`` or ``failed``. A local timeout, process
    restart, or transport exception is not itself evidence of either outcome.
    """
    if submission.state != SubmissionState.UNKNOWN.value:
        raise SubmissionRecoveryError(
            "Only an unknown submission can be reconciled"
        )
    if outcome not in {
        SubmissionState.SUBMITTED.value,
        SubmissionState.FAILED.value,
    }:
        raise SubmissionRecoveryError(
            "Unknown submissions may only reconcile to submitted or failed"
        )
    return replace(
        submission,
        state=outcome,
        submitted_at=reconciled_at if outcome == SubmissionState.SUBMITTED.value else submission.submitted_at,
        external_reference=external_reference or submission.external_reference,
        error_code=None if outcome == SubmissionState.SUBMITTED.value else submission.error_code,
        updated_at=reconciled_at,
        version=submission.version + 1,
    )


def assert_retryable_submission(submission: SubmissionRecord) -> None:
    """Fail closed unless the submission is in a known retryable state."""
    if submission.state != SubmissionState.FAILED.value:
        raise SubmissionRecoveryError(
            "Submission outcome must be reconciled before a retry"
        )
