"""Provider-neutral PostgreSQL provider for submission delivery facts."""
from __future__ import annotations

import os
from typing import Any, Callable

from src.core.submission import RECOVERABLE_SUBMISSION_STATE, SubmissionRecord


class PostgresSubmissionRepository:
    """Persist submission metadata without coupling the domain to PostgreSQL."""

    def __init__(
        self,
        *,
        connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None,
    ) -> None:
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
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS civic_case_submissions (
                        submission_id TEXT PRIMARY KEY,
                        case_id TEXT NOT NULL,
                        destination_ref TEXT NOT NULL,
                        document_ref TEXT,
                        channel TEXT NOT NULL,
                        state TEXT NOT NULL,
                        attempted_at TEXT,
                        submitted_at TEXT,
                        acknowledged_at TEXT,
                        external_reference TEXT,
                        ack_ref TEXT,
                        error_code TEXT,
                        retry_count INTEGER NOT NULL DEFAULT 0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        version INTEGER NOT NULL DEFAULT 1,
                        CONSTRAINT civic_case_submissions_retry_nonnegative CHECK (retry_count >= 0),
                        CONSTRAINT civic_case_submissions_version_positive CHECK (version > 0)
                    )
                    """
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_civic_case_submissions_case_attempted "
                    "ON civic_case_submissions(case_id, attempted_at)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_civic_case_submissions_destination "
                    "ON civic_case_submissions(destination_ref)"
                )

    def save(self, submission: SubmissionRecord) -> None:
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO civic_case_submissions (
                            submission_id, case_id, destination_ref, document_ref,
                            channel, state, attempted_at, submitted_at,
                            acknowledged_at, external_reference, ack_ref,
                            error_code, retry_count, created_at, updated_at, version
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (submission_id) DO UPDATE SET
                            case_id=EXCLUDED.case_id,
                            destination_ref=EXCLUDED.destination_ref,
                            document_ref=EXCLUDED.document_ref,
                            channel=EXCLUDED.channel,
                            state=EXCLUDED.state,
                            attempted_at=EXCLUDED.attempted_at,
                            submitted_at=EXCLUDED.submitted_at,
                            acknowledged_at=EXCLUDED.acknowledged_at,
                            external_reference=EXCLUDED.external_reference,
                            ack_ref=EXCLUDED.ack_ref,
                            error_code=EXCLUDED.error_code,
                            retry_count=EXCLUDED.retry_count,
                            created_at=EXCLUDED.created_at,
                            updated_at=EXCLUDED.updated_at,
                            version=EXCLUDED.version
                        """,
                        (
                            submission.submission_id, submission.case_id,
                            submission.destination_ref, submission.document_ref,
                            submission.channel, submission.state,
                            submission.attempted_at, submission.submitted_at,
                            submission.acknowledged_at, submission.external_reference,
                            submission.ack_ref, submission.error_code,
                            submission.retry_count, submission.created_at,
                            submission.updated_at, submission.version,
                        ),
                    )

    def get(self, submission_id: str) -> SubmissionRecord | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT submission_id, case_id, destination_ref, document_ref, channel, "
                    "state, attempted_at, submitted_at, acknowledged_at, external_reference, "
                    "ack_ref, error_code, retry_count, created_at, updated_at, version "
                    "FROM civic_case_submissions WHERE submission_id = %s",
                    (submission_id,),
                )
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    def list_for_case(self, case_id: str) -> tuple[SubmissionRecord, ...]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT submission_id, case_id, destination_ref, document_ref, channel, "
                    "state, attempted_at, submitted_at, acknowledged_at, external_reference, "
                    "ack_ref, error_code, retry_count, created_at, updated_at, version "
                    "FROM civic_case_submissions WHERE case_id = %s "
                    "ORDER BY COALESCE(attempted_at, created_at), submission_id",
                    (case_id,),
                )
                rows = cursor.fetchall()
        return tuple(self._hydrate(row) for row in rows)

    def list_recoverable(self) -> tuple[SubmissionRecord, ...]:
        """Return submissions interrupted while an external send was in flight."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT submission_id, case_id, destination_ref, document_ref, channel, "
                    "state, attempted_at, submitted_at, acknowledged_at, external_reference, "
                    "ack_ref, error_code, retry_count, created_at, updated_at, version "
                    "FROM civic_case_submissions WHERE state = %s "
                    "ORDER BY COALESCE(attempted_at, created_at), submission_id",
                    (RECOVERABLE_SUBMISSION_STATE,),
                )
                rows = cursor.fetchall()
        return tuple(self._hydrate(row) for row in rows)

    @staticmethod
    def _hydrate(row: Any) -> SubmissionRecord:
        return SubmissionRecord(
            submission_id=row[0], case_id=row[1], destination_ref=row[2],
            document_ref=row[3], channel=row[4], state=row[5],
            attempted_at=row[6], submitted_at=row[7], acknowledged_at=row[8],
            external_reference=row[9], ack_ref=row[10], error_code=row[11],
            retry_count=row[12], created_at=row[13], updated_at=row[14], version=row[15],
        )
