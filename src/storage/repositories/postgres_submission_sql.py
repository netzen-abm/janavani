"""SQL statements for the PostgreSQL submission provider."""
from src.core.submission import RECOVERABLE_SUBMISSION_STATE
from .postgres_submission_codec import SELECT_FIELDS, params
from .postgres_submission_contract import PostgresSubmissionConcurrencyError, PostgresSubmissionIdempotencyConflictError

def initialize(connection):
    with connection.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS civic_case_submissions (
            submission_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES civic_cases(case_id),
            destination_ref TEXT NOT NULL, document_ref TEXT, channel TEXT NOT NULL,
            state TEXT NOT NULL, attempted_at TIMESTAMPTZ, submitted_at TIMESTAMPTZ,
            acknowledged_at TIMESTAMPTZ, external_reference TEXT, ack_ref TEXT,
            error_code TEXT, retry_count INTEGER NOT NULL DEFAULT 0,
            version BIGINT NOT NULL DEFAULT 1, created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL, idempotency_key TEXT NOT NULL UNIQUE,
            CONSTRAINT civic_case_submissions_retry_nonnegative CHECK (retry_count >= 0),
            CONSTRAINT civic_case_submissions_version_positive CHECK (version > 0))""")
        cursor.execute("CREATE INDEX IF NOT EXISTS civic_case_submissions_case_attempted_idx ON civic_case_submissions(case_id, attempted_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS civic_case_submissions_destination_idx ON civic_case_submissions(destination_ref)")

def save(cursor, submission):
    cursor.execute(f"""INSERT INTO civic_case_submissions (
        submission_id, case_id, destination_ref, document_ref, channel, state,
        attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref,
        error_code, retry_count, version, created_at, updated_at, idempotency_key)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (submission_id) DO UPDATE SET
        case_id=EXCLUDED.case_id, destination_ref=EXCLUDED.destination_ref,
        document_ref=EXCLUDED.document_ref, channel=EXCLUDED.channel,
        state=EXCLUDED.state, attempted_at=EXCLUDED.attempted_at,
        submitted_at=EXCLUDED.submitted_at, acknowledged_at=EXCLUDED.acknowledged_at,
        external_reference=EXCLUDED.external_reference, ack_ref=EXCLUDED.ack_ref,
        error_code=EXCLUDED.error_code, retry_count=EXCLUDED.retry_count,
        version=EXCLUDED.version, created_at=EXCLUDED.created_at,
        updated_at=EXCLUDED.updated_at, idempotency_key=EXCLUDED.idempotency_key""", params(submission))

def reserve(cursor, submission):
    cursor.execute(f"""INSERT INTO civic_case_submissions (
        submission_id, case_id, destination_ref, document_ref, channel, state,
        attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref,
        error_code, retry_count, version, created_at, updated_at, idempotency_key)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (idempotency_key) DO NOTHING RETURNING {SELECT_FIELDS}""", params(submission))
    return cursor.fetchone()

def update(cursor, submission, expected_version):
    cursor.execute("""UPDATE civic_case_submissions SET
        case_id=%s,destination_ref=%s,document_ref=%s,channel=%s,state=%s,
        attempted_at=%s,submitted_at=%s,acknowledged_at=%s,external_reference=%s,
        ack_ref=%s,error_code=%s,retry_count=%s,version=%s,created_at=%s,updated_at=%s
        WHERE submission_id=%s AND version=%s AND idempotency_key=%s""",
        (submission.case_id, submission.destination_ref, submission.document_ref,
         submission.channel, submission.state, submission.attempted_at,
         submission.submitted_at, submission.acknowledged_at, submission.external_reference,
         submission.ack_ref, submission.error_code, submission.retry_count,
         submission.version, submission.created_at, submission.updated_at,
         submission.submission_id, expected_version, submission.idempotency_key))
    return cursor.rowcount

def recoverable_state():
    return RECOVERABLE_SUBMISSION_STATE
