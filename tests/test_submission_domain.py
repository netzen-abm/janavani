from datetime import timezone

import pytest

from src.domain.submission import Submission, SubmissionStatus


def test_submission_starts_as_draft_with_utc_timestamp():
    submission = Submission(case_id="case-1", document_id="doc-1")

    assert submission.status is SubmissionStatus.DRAFT
    assert submission.created_at.tzinfo is timezone.utc
    assert submission.updated_at.tzinfo is timezone.utc


def test_submission_records_each_delivery_transition():
    submission = Submission(case_id="case-1", document_id="doc-1")

    submission.transition(SubmissionStatus.APPROVED)
    submission.transition(SubmissionStatus.SUBMISSION_ATTEMPTED)
    event = submission.transition(SubmissionStatus.ACKNOWLEDGED, provider_ref="ack-123")

    assert submission.status is SubmissionStatus.ACKNOWLEDGED
    assert [item.status for item in submission.events] == [
        SubmissionStatus.APPROVED,
        SubmissionStatus.SUBMISSION_ATTEMPTED,
        SubmissionStatus.ACKNOWLEDGED,
    ]
    assert event.provider_ref == "ack-123"


def test_confirmation_requires_external_reference():
    submission = Submission(case_id="case-1")

    with pytest.raises(ValueError):
        submission.confirm(provider_ref="")

    event = submission.confirm(provider_ref="government-receipt-42")
    assert submission.status is SubmissionStatus.CONFIRMED
    assert event.provider_ref == "government-receipt-42"
