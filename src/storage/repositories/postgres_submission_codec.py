"""Submission SQL mapping helpers."""
from src.core.submission import SubmissionRecord

SELECT_FIELDS = (
    "submission_id, case_id, destination_ref, document_ref, channel, state, "
    "attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref, "
    "error_code, retry_count, version, created_at, updated_at, idempotency_key"
)
OPERATION_FIELDS = ("case_id", "destination_ref", "document_ref", "channel")

def same_operation(left, right) -> bool:
    return all(getattr(left, field) == getattr(right, field) for field in OPERATION_FIELDS)

def params(submission: SubmissionRecord):
    return (
        submission.submission_id, submission.case_id, submission.destination_ref,
        submission.document_ref, submission.channel, submission.state,
        submission.attempted_at, submission.submitted_at, submission.acknowledged_at,
        submission.external_reference, submission.ack_ref, submission.error_code,
        submission.retry_count, submission.version, submission.created_at,
        submission.updated_at, submission.idempotency_key,
    )

def hydrate(row) -> SubmissionRecord:
    return SubmissionRecord(
        submission_id=row[0], case_id=row[1], destination_ref=row[2],
        document_ref=row[3], channel=row[4], state=row[5],
        attempted_at=row[6], submitted_at=row[7], acknowledged_at=row[8],
        external_reference=row[9], ack_ref=row[10], error_code=row[11],
        retry_count=row[12], version=row[13], created_at=row[14],
        updated_at=row[15], idempotency_key=row[16],
    )
