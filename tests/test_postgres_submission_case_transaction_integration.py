from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
from src.core.submission import SubmissionRecord
from src.storage.repositories.postgres_submission_case_transaction import (
    PostgresSubmissionCaseTransactionRepository,
)
from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox
from src.storage.repositories.submission_case_transaction import SubmissionCaseConcurrencyError

ROOT = Path(__file__).parents[1]
CANONICAL_MIGRATION = ROOT / "db" / "migrations" / "20260912100000_canonical_case_policy_schema.sql"
IDEMPOTENCY_MIGRATION = ROOT / "db" / "migrations" / "20260913100000_submission_idempotency_key.sql"
TELEGRAM_INBOX_MIGRATION = ROOT / "db" / "migrations" / "20261012120000_telegram_update_inbox.sql"
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")

@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_atomic_submission_case_mutation_stale_writers_rollback_and_restart_replay():
    psycopg = pytest.importorskip("psycopg")
    canonical_sql = CANONICAL_MIGRATION.read_text(encoding="utf-8")
    idempotency_sql = IDEMPOTENCY_MIGRATION.read_text(encoding="utf-8")
    inbox_sql = TELEGRAM_INBOX_MIGRATION.read_text(encoding="utf-8")
    update_id = time.time_ns() % 9_000_000_000_000_000

    case_id = "pg-atomic-case"
    submission_id = "pg-atomic-submission"
    with psycopg.connect(DSN) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(canonical_sql)
                cursor.execute(idempotency_sql)
                cursor.execute(inbox_sql)
                cursor.execute("DELETE FROM civic_case_events WHERE case_id = %s", (case_id,))
                cursor.execute("DELETE FROM civic_case_submissions WHERE case_id = %s", (case_id,))
                cursor.execute("DELETE FROM civic_cases WHERE case_id = %s", (case_id,))
                cursor.execute(
                    """INSERT INTO civic_cases (
                        case_id, case_type, subject, narrative, created_by,
                        jurisdiction_json, subject_claims_json, status,
                        created_at, updated_at, version
                    ) VALUES (%s,%s,%s,%s,%s,'{}'::jsonb,'[]'::jsonb,%s,now(),now(),1)""",
                    (case_id, CaseType.COMPLAINT.value, "complaint", "", "pg-atomic-user", CaseStatus.READY.value),
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

    # Simulate a durably accepted Telegram update; the inbox remains incomplete
    # after the business commit to represent a worker crash in that exact window.
    inbox = PostgresTelegramInbox(dsn=DSN)
    assert inbox.accept(update_id, {"update_id": update_id, "case_id": case_id}) is True
    first_claim = inbox.claim_next()
    assert first_claim is not None and first_claim["update_id"] == update_id

    # Run the first business mutation in a separate interpreter and terminate
    # it abruptly immediately after the PostgreSQL transaction commits. The
    # inbox acknowledgement is deliberately never written by that process.
    crash_after_commit = """import os
from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
from src.core.submission import SubmissionRecord
from src.storage.repositories.postgres_submission_case_transaction import PostgresSubmissionCaseTransactionRepository

case = CivicCase(
    case_id="pg-atomic-case", case_type=CaseType.COMPLAINT, subject="Atomic test",
    narrative="Atomic persistence", created_by="pg-atomic-user",
    status=CaseStatus.SUBMITTED, created_at="2026-09-14T00:00:00+00:00",
    updated_at="2026-09-14T00:01:00+00:00", version=1,
)
submission = SubmissionRecord(
    submission_id="pg-atomic-submission", case_id="pg-atomic-case",
    destination_ref="office:test", document_ref="doc:test", channel="telegram",
    state="submitted", submitted_at="2026-09-14T00:01:00+00:00",
    created_at="2026-09-14T00:00:00+00:00", updated_at="2026-09-14T00:01:00+00:00",
    version=2, idempotency_key="pg-atomic-submission-key",
)
event = CaseEvent(
    event_id="pg-atomic-event-1", case_id="pg-atomic-case",
    event_type=CaseEventType.SUBMITTED, occurred_at="2026-09-14T00:01:00+00:00",
    actor_id="pg-atomic-user", source_channel="telegram",
)
result = PostgresSubmissionCaseTransactionRepository(
    dsn=os.environ["JANAVANI_POSTGRES_TEST_DSN"]
).persist_mutation(
    submission=submission, expected_submission_version=1,
    case=case, expected_case_version=1, event=event,
    idempotency_key=event.event_id,
)
assert result.idempotent_replay is False
assert result.submission_version == 2 and result.case_version == 2
os._exit(73)  # deliberate simulated worker crash after commit, before inbox ack
"""
    crashed = subprocess.run(
        [sys.executable, "-c", crash_after_commit],
        check=False, capture_output=True, text=True, env=os.environ.copy(),
    )
    assert crashed.returncode == 73, (
        "child must commit the mutation and then hit the deliberate crash point; "
        f"exit={crashed.returncode}, stderr={crashed.stderr}"
    )
    repository = PostgresSubmissionCaseTransactionRepository(dsn=DSN)

    with psycopg.connect(DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT state, version FROM civic_case_submissions WHERE submission_id = %s", (submission_id,))
            assert cursor.fetchone() == ("submitted", 2)
            cursor.execute("SELECT status, version FROM civic_cases WHERE case_id = %s", (case_id,))
            assert cursor.fetchone() == ("submitted", 2)
            cursor.execute("SELECT count(*) FROM civic_case_events WHERE event_id = %s", (event.event_id,))
            assert cursor.fetchone()[0] == 1

    # Simulate lease expiry and a new worker claiming the still-incomplete update.
    with psycopg.connect(DSN) as connection:
        connection.execute(
            """UPDATE public.telegram_update_inbox
               SET locked_at = now() - interval '5 minutes'
               WHERE update_id = %s""",
            (update_id,),
        )
    second_claim = inbox.claim_next(stale_after_seconds=1)
    assert second_claim is not None and second_claim["update_id"] == update_id
    assert second_claim["attempts"] == first_claim["attempts"] + 1

    replay = PostgresSubmissionCaseTransactionRepository(dsn=DSN).persist_mutation(
        submission=submission, expected_submission_version=1,
        case=case, expected_case_version=1, event=event,
        idempotency_key=event.event_id,
    )
    assert replay.idempotent_replay is True
    assert replay.case_version == 2
    assert replay.submission_version == 2
    assert replay.idempotent_replay is True
    inbox.mark_processed(update_id, attempts=second_claim["attempts"])
    with psycopg.connect(DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT status, payload FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            )
            assert cursor.fetchone() == ("processed", None)
            cursor.execute("SELECT count(*) FROM civic_case_events WHERE event_id = %s", (event.event_id,))
            assert cursor.fetchone()[0] == 1

    # A stale Case writer must not mutate either projection.
    with pytest.raises(SubmissionCaseConcurrencyError):
        repository.persist_mutation(
            submission=replace(submission, version=3), expected_submission_version=2,
            case=replace(case, version=1), expected_case_version=1,
            event=replace(event, event_id="pg-atomic-event-stale-case"),
            idempotency_key="pg-atomic-event-stale-case",
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

    # A separate interpreter verifies committed state across a process boundary.
    child_check = """import os
import psycopg

with psycopg.connect(os.environ["JANAVANI_POSTGRES_TEST_DSN"]) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT status, version FROM civic_cases WHERE case_id = %s",
            (os.environ["JANAVANI_RESTART_CASE_ID"],),
        )
        assert cursor.fetchone() == ("submitted", 2)
        cursor.execute(
            "SELECT state, version FROM civic_case_submissions WHERE submission_id = %s",
            (os.environ["JANAVANI_RESTART_SUBMISSION_ID"],),
        )
        assert cursor.fetchone() == ("submitted", 2)
        cursor.execute(
            "SELECT count(*) FROM civic_case_events WHERE event_id = %s",
            (os.environ["JANAVANI_RESTART_EVENT_ID"],),
        )
        assert cursor.fetchone()[0] == 1
"""
    child_env = {**os.environ, "JANAVANI_RESTART_CASE_ID": case_id, "JANAVANI_RESTART_SUBMISSION_ID": submission_id, "JANAVANI_RESTART_EVENT_ID": event.event_id}
    subprocess.run([sys.executable, "-c", child_check], check=True, env=child_env)
    # Terminate a real PostgreSQL backend; failed work must not break replay.
    def terminated_connection():
        connection = psycopg.connect(DSN)
        with psycopg.connect(DSN) as killer:
            killer.execute("SELECT pg_terminate_backend(%s)", (connection.info.backend_pid,))
        return connection
    with pytest.raises(psycopg.OperationalError):
        PostgresSubmissionCaseTransactionRepository(connection_factory=terminated_connection).persist_mutation(
            submission=submission, expected_submission_version=1, case=case,
            expected_case_version=1, event=event, idempotency_key=event.event_id)
    assert PostgresSubmissionCaseTransactionRepository(dsn=DSN).persist_mutation(
        submission=submission, expected_submission_version=1, case=case,
        expected_case_version=1, event=event, idempotency_key=event.event_id).idempotent_replay is True
