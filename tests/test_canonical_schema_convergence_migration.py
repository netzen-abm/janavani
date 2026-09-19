from pathlib import Path

ROOT = Path(__file__).parents[1]
SQL = (ROOT / "db/migrations/20260919_canonical_schema_convergence.sql").read_text(encoding="utf-8")


def test_convergence_is_transactional():
    assert SQL.strip().startswith("BEGIN;")
    assert SQL.strip().endswith("COMMIT;")


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
