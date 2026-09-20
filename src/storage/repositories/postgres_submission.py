"""Provider-neutral PostgreSQL provider for submission delivery facts."""
from __future__ import annotations

import os
from typing import Any, Callable

from src.core.submission import (
    RECOVERABLE_SUBMISSION_STATE,
    SubmissionConcurrencyError,
    SubmissionIdempotencyConflictError,
    SubmissionRecord,
)


_OPERATION_FIELDS = ("case_id", "destination_ref", "document_ref", "channel")


def _same_operation(left: SubmissionRecord, right: SubmissionRecord) -> bool:
    return all(getattr(left, field) == getattr(right, field) for field in _OPERATION_FIELDS)


class PostgresSubmissionRepository:
    """Persist submission metadata without coupling the domain to PostgreSQL."""

    _SELECT = (
        "submission_id, case_id, destination_ref, document_ref, channel, state, "
        "attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref, "
        "error_code, retry_count, version, created_at, updated_at, idempotency_key"
    )

    def __init__(self, *, connection_factory: Callable[[], Any] | None = None, dsn: str | None = None) -> None:
        if connection_factory is None and not (dsn or os.getenv("JANAVANI_POSTGRES_DSN")):
            raise ValueError("PostgreSQL provider requires a DSN or connection factory")
        self._connection_factory = connection_factory
        self._dsn = dsn or os.getenv("JANAVANI_POSTGRES_DSN")
        self._initialize()

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    def _initialize(self) -> None:
        """Create the canonical compatibility shape when absent."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS civic_case_submissions (
                        submission_id TEXT PRIMARY KEY,
                        case_id TEXT NOT NULL REFERENCES civic_cases(case_id),
                        destination_ref TEXT NOT NULL,
                        document_ref TEXT,
                        channel TEXT NOT NULL,
                        state TEXT NOT NULL,
                        attempted_at TIMESTAMPTZ,
                        submitted_at TIMESTAMPTZ,
                        acknowledged_at TIMESTAMPTZ,
                        external_reference TEXT,
                        ack_ref TEXT,
                        error_code TEXT,
                        retry_count INTEGER NOT NULL DEFAULT 0,
                        version BIGINT NOT NULL DEFAULT 1,
                        created_at TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL,
                        idempotency_key TEXT NOT NULL UNIQUE,
                        CONSTRAINT civic_case_submissions_retry_nonnegative CHECK (retry_count >= 0),
                        CONSTRAINT civic_case_submissions_version_positive CHECK (version > 0)
                    )
                    """
                )
                cursor.execute("CREATE INDEX IF NOT EXISTS civic_case_submissions_case_attempted_idx ON civic_case_submissions(case_id, attempted_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS civic_case_submissions_destination_idx ON civic_case_submissions(destination_ref)")

    def save(self, submission: SubmissionRecord, *, principal_id: str | None = None) -> None:
        """Compatibility save; delivery state transitions must use CAS APIs."""
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""INSERT INTO civic_case_submissions (
                            submission_id, case_id, destination_ref, document_ref, channel, state,
                            attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref,
                            error_code, retry_count, version, created_at, updated_at, idempotency_key
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (submission_id) DO UPDATE SET
                            case_id=EXCLUDED.case_id, destination_ref=EXCLUDED.destination_ref,
                            document_ref=EXCLUDED.document_ref, channel=EXCLUDED.channel, state=EXCLUDED.state,
                            attempted_at=EXCLUDED.attempted_at, submitted_at=EXCLUDED.submitted_at,
                            acknowledged_at=EXCLUDED.acknowledged_at, external_reference=EXCLUDED.external_reference,
                            ack_ref=EXCLUDED.ack_ref, error_code=EXCLUDED.error_code, retry_count=EXCLUDED.retry_count,
                            version=EXCLUDED.version, created_at=EXCLUDED.created_at, updated_at=EXCLUDED.updated_at,
                            idempotency_key=EXCLUDED.idempotency_key""",
                        self._params(submission),
                    )

    def get(self, submission_id: str, *, principal_id: str | None = None) -> SubmissionRecord | None:
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {self._SELECT} FROM civic_case_submissions WHERE submission_id = %s", (submission_id,))
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    def get_by_idempotency_key(self, idempotency_key: str, *, principal_id: str | None = None) -> SubmissionRecord | None:
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {self._SELECT} FROM civic_case_submissions WHERE idempotency_key = %s", (idempotency_key,))
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    def create_idempotent(self, submission: SubmissionRecord, *, principal_id: str | None = None) -> tuple[SubmissionRecord, bool]:
        if not submission.idempotency_key:
            raise ValueError("idempotency_key is required")
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""INSERT INTO civic_case_submissions (
                            submission_id, case_id, destination_ref, document_ref, channel, state,
                            attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref,
                            error_code, retry_count, version, created_at, updated_at, idempotency_key
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (idempotency_key) DO NOTHING RETURNING {self._SELECT}""",
                        self._params(submission),
                    )
                    row = cursor.fetchone()
                    if row is not None:
                        return self._hydrate(row), False
                    cursor.execute(f"SELECT {self._SELECT} FROM civic_case_submissions WHERE idempotency_key = %s FOR UPDATE", (submission.idempotency_key,))
                    existing_row = cursor.fetchone()
                    if existing_row is None:
                        raise RuntimeError("Submission idempotency reservation disappeared")
        existing = self._hydrate(existing_row)
        if not _same_operation(existing, submission):
            raise SubmissionIdempotencyConflictError("Idempotency key is already bound to a different submission operation")
        return existing, True

    def update_if_version(self, submission: SubmissionRecord, *, expected_version: int, principal_id: str | None = None) -> None:
        if submission.version != expected_version + 1:
            raise ValueError("Submission mutation must increment version by exactly one")
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE civic_case_submissions SET
                            case_id=%s, destination_ref=%s, document_ref=%s, channel=%s, state=%s,
                            attempted_at=%s, submitted_at=%s, acknowledged_at=%s, external_reference=%s,
                            ack_ref=%s, error_code=%s, retry_count=%s, version=%s, created_at=%s, updated_at=%s
                        WHERE submission_id=%s AND version=%s AND idempotency_key=%s""",
                        (submission.case_id, submission.destination_ref, submission.document_ref, submission.channel,
                         submission.state, submission.attempted_at, submission.submitted_at, submission.acknowledged_at,
                         submission.external_reference, submission.ack_ref, submission.error_code, submission.retry_count,
                         submission.version, submission.created_at, submission.updated_at, submission.submission_id,
                         expected_version, submission.idempotency_key),
                    )
                    if cursor.rowcount != 1:
                        cursor.execute("SELECT version FROM civic_case_submissions WHERE submission_id = %s", (submission.submission_id,))
                        row = cursor.fetchone()
                        if row is None:
                            raise LookupError("Submission not found")
                        raise SubmissionConcurrencyError(f"Submission version mismatch: expected {expected_version}, found {row[0]}")

    def list_for_case(self, case_id: str, *, principal_id: str | None = None) -> tuple[SubmissionRecord, ...]:
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {self._SELECT} FROM civic_case_submissions WHERE case_id = %s ORDER BY COALESCE(attempted_at, created_at), submission_id", (case_id,))
                rows = cursor.fetchall()
        return tuple(self._hydrate(row) for row in rows)

    def list_recoverable(self, *, principal_id: str | None = None) -> tuple[SubmissionRecord, ...]:
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {self._SELECT} FROM civic_case_submissions WHERE state = %s ORDER BY COALESCE(attempted_at, created_at), submission_id", (RECOVERABLE_SUBMISSION_STATE,))
                rows = cursor.fetchall()
        return tuple(self._hydrate(row) for row in rows)

    @staticmethod
    def _params(submission: SubmissionRecord) -> tuple[Any, ...]:
        return (
            submission.submission_id, submission.case_id, submission.destination_ref, submission.document_ref,
            submission.channel, submission.state, submission.attempted_at, submission.submitted_at,
            submission.acknowledged_at, submission.external_reference, submission.ack_ref, submission.error_code,
            submission.retry_count, submission.version, submission.created_at, submission.updated_at,
            submission.idempotency_key,
        )

    @staticmethod
    def _hydrate(row: Any) -> SubmissionRecord:
        return SubmissionRecord(
            submission_id=row[0], case_id=row[1], destination_ref=row[2], document_ref=row[3], channel=row[4],
            state=row[5], attempted_at=row[6], submitted_at=row[7], acknowledged_at=row[8], external_reference=row[9],
            ack_ref=row[10], error_code=row[11], retry_count=row[12], version=row[13], created_at=row[14],
            updated_at=row[15], idempotency_key=row[16],
        )
