from pathlib import Path
SQL = (Path(__file__).parents[1] / "db/migrations/20260919_canonical_schema_convergence.sql").read_text(encoding="utf-8")
def test_convergence_is_non_destructive():
    assert "DROP TABLE" not in SQL.upper()
    assert "DROP COLUMN" not in SQL.upper()
    assert "DELETE FROM" not in SQL.upper()
def test_case_names_converge():
    assert "RENAME COLUMN jurisdiction TO jurisdiction_json" in SQL
    assert "RENAME COLUMN claims TO subject_claims_json" in SQL
def test_submission_names_converge():
    assert "RENAME COLUMN transport TO channel" in SQL
    assert "RENAME COLUMN status TO state" in SQL
    assert "idempotency_key" in SQL
def test_rls_not_activated():
    assert "ENABLE ROW LEVEL SECURITY" not in SQL.upper()
