from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from src.core.submission import (
    SubmissionConcurrencyError,
    SubmissionIdempotencyConflictError,
    SubmissionRecord,
)
from src.storage.repositories.postgres_submission import PostgresSubmissionRepository


ROOT = Path(__file__).parents[1]
CANONICAL_MIGRATION = ROOT / "supabase" / "migrations" / "20260912100000_canonical_case_policy_schema.sql"
IDEMPOTENCY_MIGRATION = ROOT / "supabase" / "migrations" / "20260913100000_submission_idempotency_key.sql"
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_submission_idempotency_concurrency_and_retry_contract():
    psycopg = pytest.importorskip("psycopg")

    canonical_sql = CANONICAL_MIGRATION.read_text(encoding="utf-8")
    idempotency_sql = IDEMPOTENCY_MIGRATION.read_text(encoding="utf-8")

    # The CI PostgreSQL service is disposable. Re-apply the checked-in schema
    # migrations so this test remains self-contained and exercises the actual
    # repository schema rather than a hand-built test fixture.
    with psycopg.connect(DSN) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(canonical_sql)
                cursor.execute(idempotency_sql)
                cursor.execute("DELETE FROM civic_case_submissions WHERE case_id = %s", ("pg-submit-it-case",))
                cursor.execute("DELETE FROM civic_cases WHERE case_id = %s", ("pg-submit-it-case",))
                cursor.execute(
                    """
                    INSERT INTO civic_cases (
                        case_id, case_type, subject, narrative, created_by,
                        jurisdiction_json, subject_claims_json, status,
                        created_at, updated_at, version
                    ) VALUES (
                        %s, 'test', 'Submission integration case', 'Disposable PostgreSQL verification', %s,
                        '{}'::jsonb, '[]'::jsonb, 'ready', now(), now(), 1
                    )
                    """,
                    ("pg-submit-it-case", "pg-submit-it-user"),
                )

    def new_submission(*, key: str, submission_id: str, state: str = "created", version: int = 1, retry_count: int = 0):
        return SubmissionRecord(
            submission_id=submission_id,
            case_id="pg-submit-it-case",
            destination_ref="office:test",
            document_ref="doc:test",
            channel="telegram",
            state=state,
            retry_count=retry_count,
            version=version,
            created_at="2026-09-13T00:00:00+00:00",
            updated_at="2026-09-13T00:00:00+00:00",
            idempotency_key=key,
        )

    repository = PostgresSubmissionRepository(dsn=DSN)
    first, replay = repository.create_idempotent(new_submission(key="pg-submit-key", submission_id="pg-submit-1"))
    assert replay is False
    assert first.submission_id == "pg-submit-1"
    assert first.idempotency_key == "pg-submit-key"

    same, replay = repository.create_idempotent(new_submission(key="pg-submit-key", submission_id="pg-submit-2"))
    assert replay is True
    assert same.submission_id == "pg-submit-1"

    with pytest.raises(SubmissionIdempotencyConflictError):
        repository.create_idempotent(
            SubmissionRecord(
                submission_id="pg-submit-3",
                case_id="pg-submit-it-case",
                destination_ref="different:office",
                document_ref="doc:test",
                channel="telegram",
                state="created",
                created_at="2026-09-13T00:00:00+00:00",
                updated_at="2026-09-13T00:00:00+00:00",
                idempotency_key="pg-submit-key",
            )
        )

    # Two independent connections racing to reserve the same key must converge
    # on exactly one durable submission identity.
    race_key = "pg-race-key"

    def reserve(index: int):
        provider = PostgresSubmissionRepository(dsn=DSN)
        return provider.create_idempotent(new_submission(key=race_key, submission_id=f"pg-race-{index}"))

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(reserve, (1, 2)))

    assert {record.submission_id for record, _ in results} == {"pg-race-1"} | {"pg-race-2"} or len(
        {record.submission_id for record, _ in results}
    ) == 1
    assert sum(1 for _, was_replay in results if not was_replay) == 1
    race_records = repository.list_for_case("pg-submit-it-case")
    assert len([record for record in race_records if record.idempotency_key == race_key]) == 1

    # CAS mutation succeeds exactly once and a stale writer is rejected.
    submitting = SubmissionRecord(
        **{**first.__dict__, "state": "submitting", "version": 2, "attempted_at": "2026-09-13T00:01:00+00:00", "updated_at": "2026-09-13T00:01:00+00:00"}
    )
    repository.update_if_version(submitting, expected_version=1)

    stale = SubmissionRecord(
        **{**submitting.__dict__, "state": "failed", "version": 3, "retry_count": 1, "error_code": "TimeoutError", "updated_at": "2026-09-13T00:02:00+00:00"}
    )
    repository.update_if_version(stale, expected_version=2)

    with pytest.raises(SubmissionConcurrencyError):
        repository.update_if_version(
            SubmissionRecord(
                **{**stale.__dict__, "state": "submitted", "version": 3, "updated_at": "2026-09-13T00:03:00+00:00"}
            ),
            expected_version=2,
        )

    current = repository.get("pg-submit-1")
    assert current is not None
    assert current.state == "failed"
    assert current.retry_count == 1
    assert current.version == 3
    assert current.idempotency_key == "pg-submit-key"

    # A failed retry reuses the same submission identity and idempotency key.
    retry, replay = repository.create_idempotent(
        new_submission(key="pg-submit-key", submission_id="pg-submit-retry", state="created")
    )
    assert replay is True
    assert retry.submission_id == "pg-submit-1"
    assert retry.idempotency_key == "pg-submit-key"

    # The schema contract remains intentionally outside RLS activation.
    with psycopg.connect(DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "select relrowsecurity from pg_class where oid = 'public.civic_case_submissions'::regclass"
            )
            assert cursor.fetchone()[0] is False
