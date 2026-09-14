from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
from src.core.submission import SubmissionRecord
from src.storage.repositories.postgres_submission_case_transaction import (
    PostgresSubmissionCaseTransactionRepository,
)
from src.storage.repositories.submission_case_transaction import SubmissionCaseConcurrencyError

ROOT = Path(__file__).parents[1]
CANONICAL_MIGRATION = ROOT / "supabase" / "migrations" / "20260912100000_canonical_case_policy_schema.sql"
IDEMPOTENCY_MIGRATION = ROOT / "supabase" / "migrations" / "20260913100000_submission_idempotency_key.sql"
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_atomic_submission_case_mutation_stale_writers_rollback_and_restart_replay():
    psycopg = pytest.importorskip("psycopg")
    canonical_sql = CANONICAL_MIGRATION.read_text(encoding="utf-8")
    idempotency_sql = IDEMPOTENCY_MIGRATION.read_text(encoding="utf-8")

    case_id = "pg-atomic-case"
    submission_id = "pg-atomic-submission"
    with psycopg.connect(DSN) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(canonical_sql)
                cursor.execute(idempotency_sql)
                cursor.execute("DELETE FROM civic_case_events WHERE case_id = %s", (case_id,))
                cursor.execute("DELETE FROM civic_case_submissions WHERE case_id = %s", (case_id,))
                cursor.execute("DELETE FROM civic_cases WHERE case_id = %s", (case_id,))
                cursor.execute(
                    """INSERT INTO civic_cases (
                        case_id, case_type, subject, narrative, created_by,
                        jurisdiction_json, subject_claims_json, status,
                        created_at, updated_at, version
                    ) VALUES (%s,%s,%s,%s,%s,'{}'::jsonb,'[]'::jsonb,%s,now(),now(),1)""",
                    (case_id, CaseType.COMPLAINT.value, "Atomic test", "Atomic persistence", "pg-atomic-user", CaseStatus.READY.value),
                )
                cursor.execute(
                    """INSERT INTO civic_case_submissions (
                        submission_id, case_id, destination_ref, document_ref, channel, state,
                        retry_count, version, created_at, updated_at, idempotency_key
                    ) VALUES (%s,%s,%s,%s,%s,%s,0,1,now(),now(),%s)""",
                    (submission_id, case_id, "office:test", "doc:test", "telegram", "submitting", "pg-atomic-submission-key"),
                )

    case = CivicCase(
        case_id=case_id, case_type=CaseType.COMPLAINT, subject="Atomic test",
        narrative="Atomic persistence", created_by="pg-atomic-user",
        status=CaseStatus.SUBMITTED, created_at="2026-09-14T00:00:00+00:00",
        updated_at="2026-09-14T00:01:00+00:00", version=1,
    )
    submission = SubmissionRecord(
        submission_id=submission_id, case_id=case_id, destination_ref="office:test",
        document_ref="doc:test", channel="telegram", state="submitted",
        submitted_at="2026-09-14T00:01:00+00:00", created_at="2026-09-14T00:00:00+00:00",
        updated_at="2026-09-14T00:01:00+00:00", version=2,
        idempotency_key="pg-atomic-submission-key",
    )
    event = CaseEvent(
        event_id="pg-atomic-event-1", case_id=case_id, event_type=CaseEventType.SUBMITTED,
        occurred_at="2026-09-14T00:01:00+00:00", actor_id="pg-atomic-user", source_channel="telegram",
    )

    repository = PostgresSubmissionCaseTransactionRepository(dsn=DSN)
    result = repository.persist_mutation(
        submission=submission, expected_submission_version=1,
        case=case, expected_case_version=1, event=event,
        idempotency_key=event.event_id,
    )
    assert result.idempotent_replay is False
    assert result.submission_version == 2
    assert result.case_version == 2

    with psycopg.connect(DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT state, version FROM civic_case_submissions WHERE submission_id = %s", (submission_id,))
            assert cursor.fetchone() == ("submitted", 2)
            cursor.execute("SELECT status, version FROM civic_cases WHERE case_id = %s", (case_id,))
            assert cursor.fetchone() == ("submitted", 2)
            cursor.execute("SELECT count(*) FROM civic_case_events WHERE event_id = %s", (event.event_id,))
            assert cursor.fetchone()[0] == 1

    replay = PostgresSubmissionCaseTransactionRepository(dsn=DSN).persist_mutation(
        submission=submission, expected_submission_version=1,
        case=case, expected_case_version=1, event=event,
        idempotency_key=event.event_id,
    )
    assert replay.idempotent_replay is True
    assert replay.case_version == 2
    assert replay.submission_version == 2

    # A stale Case writer must not mutate either projection.
    with pytest.raises(SubmissionCaseConcurrencyError):
        repository.persist_mutation(
            submission=replace(submission, version=3), expected_submission_version=2,
            case=replace(case, version=1), expected_case_version=1,
            event=replace(event, event_id="pg-atomic-event-stale-case"),
            idempotency_key="pg-atomic-event-stale-case",
        )

    # A stale Submission writer is checked after the Case UPDATE in the SQL
    # transaction; rollback must undo that preceding Case mutation too.
    with pytest.raises(SubmissionCaseConcurrencyError):
        repository.persist_mutation(
            submission=replace(submission, version=3), expected_submission_version=1,
            case=replace(case, status=CaseStatus.SUBMITTED, version=2), expected_case_version=2,
            event=replace(event, event_id="pg-atomic-event-stale-submission"),
            idempotency_key="pg-atomic-event-stale-submission",
        )

    # Force the lifecycle-event INSERT to fail after both projections have
    # been changed. PostgreSQL transaction rollback must remove both changes.
    invalid_event = SimpleNamespace(
        event_id="pg-atomic-event-rollback",
        case_id=case_id,
        event_type=SimpleNamespace(value=None),
        occurred_at="2026-09-14T00:02:00+00:00",
        actor_id="pg-atomic-user",
        source_channel="telegram",
        source_ref=None,
        notes="forced rollback test",
    )
    with pytest.raises(Exception):
        repository.persist_mutation(
            submission=replace(submission, state="acknowledged", acknowledged_at="2026-09-14T00:02:00+00:00", version=3),
            expected_submission_version=2,
            case=replace(case, status=CaseStatus.ACKNOWLEDGED, version=3),
            expected_case_version=2,
            event=invalid_event,
            idempotency_key=invalid_event.event_id,
        )

    with psycopg.connect(DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT status, version FROM civic_cases WHERE case_id = %s", (case_id,))
            assert cursor.fetchone() == ("submitted", 2)
            cursor.execute("SELECT state, version FROM civic_case_submissions WHERE submission_id = %s", (submission_id,))
            assert cursor.fetchone() == ("submitted", 2)
            cursor.execute("SELECT count(*) FROM civic_case_events WHERE event_id = %s", (invalid_event.event_id,))
            assert cursor.fetchone()[0] == 0

    # A fresh repository instance after the committed transaction must still
    # converge on the exact durable state through idempotent replay.
    restarted = PostgresSubmissionCaseTransactionRepository(dsn=DSN)
    replay_after_restart = restarted.persist_mutation(
        submission=submission, expected_submission_version=1,
        case=case, expected_case_version=1, event=event,
        idempotency_key=event.event_id,
    )
    assert replay_after_restart.idempotent_replay is True
    assert replay_after_restart.case_version == 2
    assert replay_after_restart.submission_version == 2

    with psycopg.connect(DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version FROM civic_cases WHERE case_id = %s", (case_id,))
            assert cursor.fetchone()[0] == 2
            cursor.execute("SELECT version FROM civic_case_submissions WHERE submission_id = %s", (submission_id,))
            assert cursor.fetchone()[0] == 2
