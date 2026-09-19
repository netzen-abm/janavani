from __future__ import annotations

import os
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
RLS_SQL = (ROOT / "db/migrations/CANDIDATE_20260919_rls_authorization.sql").read_text(
    encoding="utf-8"
)
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")


pytestmark = pytest.mark.skipif(
    not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN"
)


def _bootstrap(connection):
    canonical = (
        ROOT / "db/migrations/20260912100000_canonical_case_policy_schema.sql"
    ).read_text(encoding="utf-8")
    idempotency = (
        ROOT / "db/migrations/20260913100000_submission_idempotency_key.sql"
    ).read_text(encoding="utf-8")
    with connection.cursor() as cur:
        cur.execute(canonical)
        cur.execute(idempotency)


def _set_principal(connection, principal: str):
    with connection.cursor() as cur:
        cur.execute("SELECT set_config('janavani.principal_id', %s, false)", (principal,))


def _role_name(prefix: str) -> str:
    return prefix.replace("-", "_")


def test_candidate_rls_real_postgres_owner_delegate_and_isolation():
    psycopg = pytest.importorskip("psycopg")
    owner_role = _role_name("janavani_rls_owner")
    delegate_role = _role_name("janavani_rls_delegate")
    stranger_role = _role_name("janavani_rls_stranger")

    with psycopg.connect(DSN, autocommit=True) as admin:
        with admin.cursor() as cur:
            for role in (owner_role, delegate_role, stranger_role):
                cur.execute(f"DROP ROLE IF EXISTS {role}")
                cur.execute(f"CREATE ROLE {role} NOLOGIN")
            cur.execute(f"GRANT USAGE ON SCHEMA public, janavani_private TO {owner_role}, {delegate_role}, {stranger_role}")
            cur.execute(f"GRANT SELECT, INSERT, UPDATE ON public.civic_cases TO {owner_role}, {delegate_role}, {stranger_role}")
            cur.execute(f"GRANT SELECT ON public.janavani_delegation_grants TO {owner_role}, {delegate_role}, {stranger_role}")
            cur.execute(f"GRANT SELECT ON public.civic_case_consents TO {owner_role}, {delegate_role}, {stranger_role}")
            cur.execute(f"GRANT SELECT ON public.janavani_service_identity_policies TO {owner_role}, {delegate_role}, {stranger_role}")

    try:
        with psycopg.connect(DSN) as connection:
            with connection.transaction():
                _bootstrap(connection)
                with connection.cursor() as cur:
                    cur.execute("ALTER TABLE public.civic_cases ENABLE ROW LEVEL SECURITY")
                    cur.execute("ALTER TABLE public.civic_case_consents ENABLE ROW LEVEL SECURITY")
                    cur.execute("ALTER TABLE public.janavani_delegation_grants ENABLE ROW LEVEL SECURITY")
                    cur.execute("ALTER TABLE public.janavani_service_identity_policies ENABLE ROW LEVEL SECURITY")
                    cur.execute(RLS_SQL)
                    cur.execute(
                        """
                        INSERT INTO civic_cases (
                            case_id, case_type, subject, narrative, created_by,
                            jurisdiction_json, subject_claims_json, status,
                            created_at, updated_at, version
                        ) VALUES (
                            'rls-case', 'complaint', 'RLS test', 'Authorization test',
                            'alice', '{}'::jsonb, '[]'::jsonb, 'ready', now(), now(), 1
                        )
                        """
                    )
                    cur.execute(
                        """
                        INSERT INTO civic_case_consents (
                            consent_id, case_id, purpose, scope, status,
                            subject_id, created_at
                        ) VALUES (
                            'rls-consent', 'rls-case', 'test', '{}'::jsonb,
                            'active', 'alice', now()
                        )
                        """
                    )
                    cur.execute(
                        """
                        INSERT INTO janavani_delegation_grants (
                            delegation_id, grantor_id, delegate_id, capabilities,
                            actions, resource_ids, expires_at, revoked
                        ) VALUES (
                            'rls-delegation', 'alice', 'bob', '[]'::jsonb,
                            '[\"case:update\"]'::jsonb,
                            '[\"rls-case\"]'::jsonb,
                            now() + interval '1 hour', false
                        )
                        """
                    )
                    cur.execute(
                        """
                        INSERT INTO janavani_service_identity_policies (
                            principal_id, allowed_capabilities, allowed_actions
                        ) VALUES ('service-a', '[]'::jsonb, '[]'::jsonb)
                        """
                    )

        # Application roles are deliberately NOLOGIN and therefore cannot be
        # used through a second database connection without an explicit role
        # switch. Test RLS semantics by SET ROLE from the owning test session.
        with psycopg.connect(DSN) as connection:
            with connection.transaction():
                with connection.cursor() as cur:
                    cur.execute("SET ROLE " + owner_role)
                    _set_principal(connection, "alice")
                    cur.execute("SELECT count(*) FROM civic_cases WHERE case_id = 'rls-case'")
                    assert cur.fetchone()[0] == 1

                    cur.execute("SET ROLE " + delegate_role)
                    _set_principal(connection, "bob")
                    cur.execute("SELECT count(*) FROM civic_cases WHERE case_id = 'rls-case'")
                    assert cur.fetchone()[0] == 1
                    cur.execute(
                        "UPDATE civic_cases SET narrative = 'delegate update', version = 2 WHERE case_id = 'rls-case'"
                    )
                    assert cur.rowcount == 1

                    cur.execute("SET ROLE " + stranger_role)
                    _set_principal(connection, "mallory")
                    cur.execute("SELECT count(*) FROM civic_cases WHERE case_id = 'rls-case'")
                    assert cur.fetchone()[0] == 0
                    cur.execute(
                        "UPDATE civic_cases SET narrative = 'cross-user update' WHERE case_id = 'rls-case'"
                    )
                    assert cur.rowcount == 0
                    cur.execute("SELECT count(*) FROM civic_case_consents WHERE consent_id = 'rls-consent'")
                    assert cur.fetchone()[0] == 0
                    cur.execute("SELECT count(*) FROM janavani_service_identity_policies")
                    assert cur.fetchone()[0] == 0

                    cur.execute("SET ROLE " + delegate_role)
                    _set_principal(connection, "bob")
                    cur.execute(
                        "UPDATE janavani_delegation_grants SET revoked = true WHERE delegation_id = 'rls-delegation'"
                    )
                    assert cur.rowcount == 0

    finally:
        with psycopg.connect(DSN, autocommit=True) as admin:
            with admin.cursor() as cur:
                for role in (owner_role, delegate_role, stranger_role):
                    cur.execute(f"DROP ROLE IF EXISTS {role}")
