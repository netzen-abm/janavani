from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest


ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
BASE_SCHEMA = (ROOT / "db/migrations/20260912100000_canonical_case_policy_schema.sql").read_text(encoding="utf-8")
IDENTITY_SCHEMA = (ROOT / "db/migrations/20260920100000_external_identity_links.sql").read_text(encoding="utf-8")
RLS_POLICY = (ROOT / "db/migrations/CANDIDATE_20260919_rls_authorization.sql").read_text(encoding="utf-8")


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_live_postgres_rls_cross_user_case_isolation_and_owner_integrity():
    psycopg = pytest.importorskip("psycopg")
    role = "janavani_rls_" + uuid4().hex[:12]
    password = "test-password-" + uuid4().hex

    with psycopg.connect(DSN) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(BASE_SCHEMA)
                cursor.execute(IDENTITY_SCHEMA)
                cursor.execute(RLS_POLICY)

                cursor.execute(
                    f'CREATE ROLE "{role}" LOGIN PASSWORD %s NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS',
                    (password,),
                )
                cursor.execute(f'GRANT USAGE ON SCHEMA public TO "{role}"')
                cursor.execute(
                    f'GRANT SELECT, INSERT, UPDATE ON public.civic_cases TO "{role}"'
                )
                cursor.execute(
                    f'GRANT SELECT, INSERT, UPDATE ON public.civic_case_consents TO "{role}"'
                )

                case_id = "rls-case-" + uuid4().hex
                now_sql = "now()"

                cursor.execute(f'SET ROLE "{role}"')
                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-a",))

                cursor.execute(
                    f"""
                    INSERT INTO public.civic_cases
                    (case_id, case_type, subject, narrative, created_by, status, created_at, updated_at)
                    VALUES (%s, 'complaint', 'A subject', 'A narrative', %s, 'draft', {now_sql}, {now_sql})
                    """,
                    (case_id, "principal-a"),
                )

                cursor.execute(
                    "SELECT case_id FROM public.civic_cases WHERE case_id = %s",
                    (case_id,),
                )
                assert cursor.fetchone()[0] == case_id

                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-b",))
                cursor.execute(
                    "SELECT case_id FROM public.civic_cases WHERE case_id = %s",
                    (case_id,),
                )
                assert cursor.fetchone() is None

                with connection.transaction():
                    with pytest.raises(psycopg.errors.InsufficientPrivilege):
                        cursor.execute(
                            """
                            INSERT INTO public.civic_cases
                            (case_id, case_type, subject, narrative, created_by, status, created_at, updated_at)
                            VALUES (%s, 'complaint', 'B subject', 'B narrative', %s, 'draft', now(), now())
                            """,
                            ("rls-forged-" + uuid4().hex, "principal-a"),
                        )

                cursor.execute(
                    "UPDATE public.civic_cases SET subject = 'B must not mutate A' WHERE case_id = %s",
                    (case_id,),
                )
                assert cursor.rowcount == 0

                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-a",))
                cursor.execute(
                    "UPDATE public.civic_cases SET subject = 'A can mutate A' WHERE case_id = %s",
                    (case_id,),
                )
                assert cursor.rowcount == 1

                cursor.execute("RESET ROLE")
                cursor.execute(f'DROP ROLE "{role}"')
