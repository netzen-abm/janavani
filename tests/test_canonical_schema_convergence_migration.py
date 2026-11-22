from pathlib import Path

ROOT = Path(__file__).parents[1]
SQL = (ROOT / "db/migrations/20260919_canonical_schema_convergence.sql").read_text(encoding="utf-8")


def _sql_without_leading_comments(sql: str) -> str:
    lines = sql.splitlines()
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("--")):
        lines.pop(0)
    return "\n".join(lines)


def test_convergence_is_transactional():
    statements = _sql_without_leading_comments(SQL)
    assert statements.startswith("BEGIN;")
    assert statements.rstrip().endswith("COMMIT;")


def test_case_legacy_names_converge_to_canonical_names():
    assert "RENAME COLUMN jurisdiction TO jurisdiction_json" in SQL
    assert "RENAME COLUMN claims TO subject_claims_json" in SQL


def test_submission_legacy_names_converge_to_canonical_names():
    assert "RENAME COLUMN transport TO channel" in SQL
    assert "RENAME COLUMN status TO state" in SQL


def test_submission_idempotency_is_enforced():
    assert "idempotency_key" in SQL
    assert "civic_case_submissions_idempotency_key_uidx" in SQL


def test_event_metadata_is_supported():
    assert "ADD COLUMN IF NOT EXISTS metadata_json jsonb" in SQL


ACTION_IDEMPOTENCY = (
    ROOT / "db" / "migrations" / "20261122120000_consent_action_fingerprint.sql"
).read_text(encoding="utf-8")


def test_consent_action_idempotency_migration_is_additive_and_unique():
    normalized = _sql_without_leading_comments(ACTION_IDEMPOTENCY).upper()
    assert normalized.startswith("BEGIN;")
    assert normalized.rstrip().endswith("COMMIT;")
    assert "ADD COLUMN IF NOT EXISTS ACTION_FINGERPRINT TEXT" in normalized
    assert "CREATE UNIQUE INDEX IF NOT EXISTS CIVIC_CASE_CONSENTS_SUBJECT_ACTION_UIDX" in normalized
    assert "ON PUBLIC.CIVIC_CASE_CONSENTS (SUBJECT_ID, ACTION_FINGERPRINT)" in normalized
    assert "WHERE ACTION_FINGERPRINT IS NOT NULL" in normalized
    assert "DROP TABLE" not in normalized
    assert "DELETE FROM" not in normalized
