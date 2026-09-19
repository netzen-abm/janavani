import json
from pathlib import Path


def test_supabase_atomic_write_migration_uses_live_schema_names():
    sql = Path("supabase/migrations/20260919123000_civic_case_atomic_write_boundary.sql").read_text(encoding="utf-8")
    for token in ("civic_cases", "civic_case_events", "civic_case_evidence_refs", "civic_case_document_refs", "jurisdiction", "claims", "service_role"):
        assert token in sql
    assert "jurisdiction_json" not in sql
    assert "subject_claims_json" not in sql
    assert "enable row level security" not in sql.lower()


def test_supabase_atomic_write_is_not_granted_to_client_roles():
    sql = Path("supabase/migrations/20260919123000_civic_case_atomic_write_boundary.sql").read_text(encoding="utf-8")
    assert "revoke all on function" in sql.lower()
    assert "from public, anon, authenticated" in sql.lower()
    assert "grant execute on function" in sql.lower()
    assert "to service_role" in sql.lower()
