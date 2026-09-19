from pathlib import Path


MIGRATION = Path(__file__).parents[1] / "db" / "migrations" / "20260913100000_submission_idempotency_key.sql"
REPOSITORY = Path(__file__).parents[1] / "src" / "storage" / "repositories" / "postgres_submission.py"


def test_submission_idempotency_migration_is_additive_and_unique() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()
    assert "add column if not exists idempotency_key text" in sql
    assert "set idempotency_key = submission_id" in sql
    assert "alter column idempotency_key set not null" in sql
    assert "create unique index if not exists civic_case_submissions_idempotency_key_uidx" in sql
    assert "enable row level security" not in sql


def test_postgres_provider_has_atomic_idempotency_and_cas_boundaries() -> None:
    source = REPOSITORY.read_text(encoding="utf-8")
    assert "ON CONFLICT (idempotency_key) DO NOTHING RETURNING" in source
    assert "WHERE submission_id=%s AND version=%s AND idempotency_key=%s" in source
    assert "SubmissionConcurrencyError" in source
    assert "SubmissionIdempotencyConflictError" in source
