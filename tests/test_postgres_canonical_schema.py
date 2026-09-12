from __future__ import annotations

import os
from pathlib import Path

import pytest


MIGRATION = Path(__file__).parents[1] / "supabase" / "migrations" / "20260912100000_canonical_case_policy_schema.sql"
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_canonical_schema_migration_creates_required_tables_and_constraints():
    psycopg = pytest.importorskip("psycopg")
    sql = MIGRATION.read_text(encoding="utf-8")

    with psycopg.connect(DSN) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cursor.execute(
                    """
                    select table_name
                    from information_schema.tables
                    where table_schema = 'public'
                      and table_name = any(%s)
                    order by table_name
                    """,
                    (
                        [
                            "civic_cases",
                            "civic_case_events",
                            "civic_case_consents",
                            "civic_case_evidence_refs",
                            "civic_case_document_refs",
                            "civic_case_submissions",
                            "civic_case_audit",
                            "janavani_delegation_grants",
                            "janavani_service_identity_policies",
                        ],
                    ),
                )
                tables = {row[0] for row in cursor.fetchall()}

                assert tables == {
                    "civic_cases",
                    "civic_case_events",
                    "civic_case_consents",
                    "civic_case_evidence_refs",
                    "civic_case_document_refs",
                    "civic_case_submissions",
                    "civic_case_audit",
                    "janavani_delegation_grants",
                    "janavani_service_identity_policies",
                }

                cursor.execute(
                    "select relrowsecurity from pg_class where oid = 'public.civic_cases'::regclass"
                )
                assert cursor.fetchone()[0] is False

                cursor.execute(
                    "select relrowsecurity from pg_class where oid = 'public.civic_case_consents'::regclass"
                )
                assert cursor.fetchone()[0] is False
