from dataclasses import replace

import pytest

from src.core.submission import SubmissionRecord
from src.core.submission_recovery import (
    SubmissionRecoveryError,
    assert_retryable_submission,
    mark_interrupted_submission_unknown,
    reconcile_unknown_submission,
)


def make_submission(state: str = "submitting") -> SubmissionRecord:
    return SubmissionRecord(
        submission_id="sub_1",
        case_id="case_1",
        destination_ref="office_1",
        document_ref="doc_1",
        channel="telegram",
        state=state,
        attempted_at="2026-09-12T10:00:00+00:00",
        created_at="2026-09-12T09:59:00+00:00",
        updated_at="2026-09-12T10:00:00+00:00",
        version=2,
    )


def test_interrupted_submission_becomes_unknown_without_claiming_success():
    recovered = mark_interrupted_submission_unknown(
        make_submission(), recovered_at="2026-09-12T10:05:00+00:00"
    )

    assert recovered.state == "unknown"
    assert recovered.error_code == "unknown_outcome_after_restart"
    assert recovered.retry_count == 0
    assert recovered.version == 3
    assert recovered.submitted_at is None


def test_unknown_submission_cannot_be_retried_before_reconciliation():
    unknown = mark_interrupted_submission_unknown(
        make_submission(), recovered_at="2026-09-12T10:05:00+00:00"
    )

    with pytest.raises(SubmissionRecoveryError):
        assert_retryable_submission(unknown)


def test_unknown_submission_can_reconcile_to_verified_submission():
    unknown = mark_interrupted_submission_unknown(
        make_submission(), recovered_at="2026-09-12T10:05:00+00:00"
    )
    reconciled = reconcile_unknown_submission(
        unknown,
        outcome="submitted",
        reconciled_at="2026-09-12T10:06:00+00:00",
        external_reference="EXT-123",
    )

    assert reconciled.state == "submitted"
    assert reconciled.external_reference == "EXT-123"
    assert reconciled.submitted_at == "2026-09-12T10:06:00+00:00"
    assert reconciled.version == 4
    with pytest.raises(SubmissionRecoveryError):
        assert_retryable_submission(reconciled)


def test_unknown_submission_can_reconcile_to_failure_then_be_retryable():
    unknown = mark_interrupted_submission_unknown(
        make_submission(), recovered_at="2026-09-12T10:05:00+00:00"
    )
    failed = reconcile_unknown_submission(
        unknown,
        outcome="failed",
        reconciled_at="2026-09-12T10:07:00+00:00",
    )

    assert failed.state == "failed"
    assert failed.version == 4
    assert_retryable_submission(failed)


def test_invalid_recovery_transitions_fail_closed():
    with pytest.raises(SubmissionRecoveryError):
        mark_interrupted_submission_unknown(
            make_submission("created"), recovered_at="2026-09-12T10:05:00+00:00"
        )

    with pytest.raises(SubmissionRecoveryError):
        reconcile_unknown_submission(
            make_submission("submitted"),
            outcome="submitted",
            reconciled_at="2026-09-12T10:06:00+00:00",
        )

    unknown = mark_interrupted_submission_unknown(
        make_submission(), recovered_at="2026-09-12T10:05:00+00:00"
    )
    with pytest.raises(SubmissionRecoveryError):
        reconcile_unknown_submission(
            unknown,
            outcome="acknowledged",
            reconciled_at="2026-09-12T10:06:00+00:00",
        )
