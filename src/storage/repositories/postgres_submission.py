"""Provider-neutral PostgreSQL provider for submission delivery facts."""
from __future__ import annotations
import os
from typing import Any, Callable
from src.storage.postgres_unit_of_work import bind_postgres_principal
from src.core.submission import (\n    RECOVERABLE_SUBMISSION_STATE, SubmissionRecord, SubmissionConcurrencyError,\n    SubmissionIdempotencyConflictError,\n)
from src.storage.repositories.postgres_submission_codec import SELECT_FIELDS, hydrate, same_operation
from src.storage.repositories.postgres_submission_sql import (
    initialize, recoverable_state, reserve, save, update,
)
from src.storage.repositories.postgres_submission_contract import (
    PostgresSubmissionConcurrencyError, PostgresSubmissionIdempotencyConflictError,
    PostgresSubmissionPersistenceError,
)

class PostgresSubmissionRepository:
    """Persist submission metadata without coupling the domain to PostgreSQL."""

    def __init__(self, *, connection_factory: Callable[[], Any] | None = None,
                 dsn: str | None = None) -> None:
        if connection_factory is None and not (dsn or os.getenv("JANAVANI_POSTGRES_DSN")):
            raise ValueError("PostgreSQL provider requires a DSN or connection factory")
        self._connection_factory = connection_factory
        self._dsn = dsn or os.getenv("JANAVANI_POSTGRES_DSN")
        self._initialize()

    def _connect(self):
        if self._connection_factory is not None:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise PostgresSubmissionPersistenceError("Psycopg 3 is required") from exc
        return psycopg.connect(self._dsn)

    def _initialize(self):
        with self._connect() as connection:
            initialize(connection)

    def save(self, submission: SubmissionRecord, *, principal_id: str | None = None) -> None:
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.transaction():
                with connection.cursor() as cursor:
                    save(cursor, submission)

    def get(self, submission_id: str, *, principal_id: str | None = None):
        return self._get("submission_id = %s", (submission_id,), principal_id)

    def get_by_idempotency_key(self, idempotency_key: str, *, principal_id: str | None = None):
        return self._get("idempotency_key = %s", (idempotency_key,), principal_id)

    def _get(self, predicate, params, principal_id):
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {SELECT_FIELDS} FROM civic_case_submissions WHERE {predicate}", params)
                row = cursor.fetchone()
        return hydrate(row) if row else None

    def create_idempotent(self, submission: SubmissionRecord, *, principal_id: str | None = None):
        if not submission.idempotency_key:
            raise ValueError("idempotency_key is required")
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.transaction():
                with connection.cursor() as cursor:
                    row = reserve(cursor, submission)
                    if row is not None:
                        return hydrate(row), False
                    cursor.execute(
                        f"SELECT {SELECT_FIELDS} FROM civic_case_submissions "
                        "WHERE idempotency_key = %s FOR UPDATE",
                        (submission.idempotency_key,),
                    )
                    existing_row = cursor.fetchone()
                    if existing_row is None:
                        raise PostgresSubmissionPersistenceError(
                            "Submission idempotency reservation disappeared"
                        )
        existing = hydrate(existing_row)
        if not same_operation(existing, submission):
            raise PostgresSubmissionIdempotencyConflictError(
                "Idempotency key is already bound to a different submission operation"
            )
        return existing, True

    def update_if_version(self, submission: SubmissionRecord, *,
                          expected_version: int, principal_id: str | None = None):
        if submission.version != expected_version + 1:
            raise ValueError("Submission mutation must increment version by exactly one")
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.transaction():
                with connection.cursor() as cursor:
                    if update(cursor, submission, expected_version) != 1:
                        self._raise_concurrency(cursor, submission, expected_version)

    @staticmethod
    def _raise_concurrency(cursor, submission, expected_version):
        cursor.execute(
            "SELECT version FROM civic_case_submissions WHERE submission_id = %s",
            (submission.submission_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise LookupError("Submission not found")
        raise PostgresSubmissionConcurrencyError(
            f"Submission version mismatch: expected {expected_version}, found {row[0]}"
        )

    def list_for_case(self, case_id: str, *, principal_id: str | None = None):
        return self._list("case_id = %s", (case_id,), principal_id)

    def list_recoverable(self, *, principal_id: str | None = None):
        return self._list("state = %s", (recoverable_state(),), principal_id)

    def _list(self, predicate, params, principal_id):
        with self._connect() as connection:
            bind_postgres_principal(connection, principal_id)
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT {SELECT_FIELDS} FROM civic_case_submissions "
                    f"WHERE {predicate} ORDER BY COALESCE(attempted_at, created_at), submission_id",
                    params,
                )
                rows = cursor.fetchall()
        return tuple(hydrate(row) for row in rows)
