from pathlib import Path

ROOT = Path(__file__).parents[1]
SQL = (ROOT / "db/migrations/CANDIDATE_20260919_rls_authorization.sql").read_text(encoding="utf-8")


def _sql_without_line_comments(sql: str) -> str:
    return "\n".join(line for line in sql.splitlines() if not line.lstrip().startswith("--"))


def test_candidate_rls_is_not_implicitly_activated():
    assert "STATUS: CANDIDATE ONLY / NOT ACTIVATED" in SQL


def test_candidate_uses_janavani_opaque_principal_context():
    executable_sql = _sql_without_line_comments(SQL)
    assert "current_setting('janavani.principal_id', true)" in executable_sql
    assert "auth.uid()" not in executable_sql


def test_case_insert_cannot_choose_another_owner():
    assert "created_by = janavani_private.current_principal_id()" in SQL


def test_case_update_has_with_check_owner_invariant():
    assert "WITH CHECK (" in SQL
    assert "created_by = janavani_private.current_principal_id()" in SQL


def test_service_policy_table_is_not_open_to_client_roles():
    assert "REVOKE ALL ON public.janavani_service_identity_policies FROM anon, authenticated;" in SQL
