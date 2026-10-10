from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
from psycopg import sql

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
BASE_SCHEMA = (ROOT / "db/migrations/20260912100000_canonical_case_policy_schema.sql").read_text(encoding="utf-8")
IDENTITY_SCHEMA = (ROOT / "db/migrations/20260920100000_external_identity_links.sql").read_text(encoding="utf-8")
RLS_POLICY = (ROOT / "db/migrations/CANDIDATE_20260919_rls_authorization.sql").read_text(encoding="utf-8")


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_live_postgres_rls_cross_surface_resource_isolation():
    psycopg = pytest.importorskip("psycopg")
    role = "janavani_rls_" + uuid4().hex[:12]
    password = "test-password-" + uuid4().hex
    case_id = "rls-case-" + uuid4().hex
    evidence_id = "rls-evidence-" + uuid4().hex
    document_id = "rls-document-" + uuid4().hex
    artifact_id = "rls-artifact-" + uuid4().hex
    consent_id = "rls-consent-" + uuid4().hex
    submission_id = "rls-submission-" + uuid4().hex

    with psycopg.connect(DSN) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(BASE_SCHEMA)
                cursor.execute(IDENTITY_SCHEMA)
                cursor.execute(RLS_POLICY)

                cursor.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS").format(
                        sql.Identifier(role), sql.Literal(password)
                    )
                )
                cursor.execute(
                    "CREATE ROLE janavani_identity_service NOLOGIN "
                    "NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS"
                )
                cursor.execute(f'GRANT USAGE ON SCHEMA public TO "{role}"')
                cursor.execute(f'GRANT SELECT, INSERT, UPDATE ON public.civic_cases TO "{role}"')
                cursor.execute(f'GRANT SELECT, INSERT, UPDATE ON public.civic_case_consents TO "{role}"')
                cursor.execute(f'GRANT SELECT, INSERT, UPDATE ON public.civic_case_submissions TO "{role}"')
                cursor.execute(f'GRANT SELECT, INSERT ON public.civic_case_evidence_refs, public.civic_case_document_refs TO "{role}"')
                cursor.execute(f'GRANT SELECT ON public.evidence_objects, public.document_artifacts TO "{role}"')
                # Ordinary application roles can reach the table but cannot
                # enumerate identity mappings. The dedicated trusted role is
                # the only role authorized by the identity RLS policy.
                cursor.execute(f'GRANT SELECT, INSERT, UPDATE ON public.external_identity_links TO "{role}"')
                cursor.execute("GRANT USAGE ON SCHEMA public TO janavani_identity_service")
                cursor.execute("GRANT SELECT, INSERT, UPDATE ON public.external_identity_links TO janavani_identity_service")

                # Seed backend-owned case/evidence/document metadata before
                # switching to the restricted application role. Ordinary clients
                # cannot register evidence/document metadata directly under the
                # candidate policy.
                cursor.execute(
                    "INSERT INTO public.external_identity_links "
                    "(provider, subject, principal_id, authentication_method, verified) "
                    "VALUES ('telegram', 'identity-rls-subject', 'principal-a', 'test', true)"
                )
                cursor.execute(
                    """
                    INSERT INTO public.civic_cases
                    (case_id, case_type, subject, narrative, created_by, status, created_at, updated_at)
                    VALUES (%s, 'complaint', 'complaint', '', %s, 'draft', now(), now())
                    """,
                    (case_id, "principal-a"),
                )
                cursor.execute(
                    """
                    INSERT INTO public.evidence_objects
                    (evidence_id, evidence_type, storage_ref, sha256, received_at, status)
                    VALUES (%s, 'document', 'local:test-evidence', 'sha256:test', now(), 'active')
                    """,
                    (evidence_id,),
                )
                cursor.execute(
                    """
                    INSERT INTO public.document_artifacts
                    (artifact_id, document_id, case_id, format, storage_ref, state)
                    VALUES (%s, %s, %s, 'text/plain', 'local:test-document', 'draft')
                    """,
                    (artifact_id, document_id, case_id),
                )
                cursor.execute(f'SET ROLE "{role}"')
                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-a",))
                cursor.execute(
                    "SELECT principal_id FROM public.external_identity_links "
                    "WHERE provider = 'telegram' AND subject = 'identity-rls-subject'"
                )
                assert cursor.fetchone() is None
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with connection.transaction():
                        cursor.execute(
                            "INSERT INTO public.external_identity_links "
                            "(provider, subject, principal_id, authentication_method, verified) "
                            "VALUES ('forged', 'subject', 'principal-a', 'test', true)"
                        )
                cursor.execute("SET ROLE janavani_identity_service")
                cursor.execute(
                    "SELECT principal_id FROM public.external_identity_links "
                    "WHERE provider = 'telegram' AND subject = 'identity-rls-subject'"
                )
                assert cursor.fetchone()[0] == "principal-a"
                cursor.execute("RESET ROLE")
                cursor.execute("SET ROLE " + role)
                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-a",))
                cursor.execute(
                    """
                    INSERT INTO public.civic_case_evidence_refs
                    (case_id, evidence_id, relationship, created_at, created_by)
                    VALUES (%s, %s, 'primary', now(), %s)
                    """,
                    (case_id, evidence_id, "principal-a"),
                )
                cursor.execute(
                    """
                    INSERT INTO public.civic_case_consents
                    (consent_id, case_id, purpose, scope, status, subject_id, created_at)
                    VALUES (%s, %s, 'case-test', '{}'::jsonb, 'active', %s, now())
                    """,
                    (consent_id, case_id, "principal-a"),
                )
                cursor.execute(
                    """
                    INSERT INTO public.civic_case_submissions
                    (submission_id, case_id, destination_ref, channel, state, idempotency_key, created_at, updated_at)
                    VALUES (%s, %s, 'destination:test', 'test', 'pending', %s, now(), now())
                    """,
                    (submission_id, case_id, "rls-idempotency-" + submission_id),
                )

                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-b",))

                cursor.execute("SELECT case_id FROM public.civic_cases WHERE case_id = %s", (case_id,))
                assert cursor.fetchone() is None

                cursor.execute("SELECT evidence_id FROM public.evidence_objects WHERE evidence_id = %s", (evidence_id,))
                assert cursor.fetchone() is None

                cursor.execute("SELECT artifact_id FROM public.document_artifacts WHERE artifact_id = %s", (artifact_id,))
                assert cursor.fetchone() is None

                cursor.execute("SELECT evidence_id FROM public.civic_case_evidence_refs WHERE case_id = %s", (case_id,))
                assert cursor.fetchall() == []

                cursor.execute("SELECT document_id FROM public.civic_case_document_refs WHERE case_id = %s", (case_id,))
                assert cursor.fetchall() == []

                cursor.execute("SELECT consent_id FROM public.civic_case_consents WHERE consent_id = %s", (consent_id,))
                assert cursor.fetchone() is None

                cursor.execute("SELECT submission_id FROM public.civic_case_submissions WHERE submission_id = %s", (submission_id,))
                assert cursor.fetchone() is None

                with pytest.raises((psycopg.errors.InsufficientPrivilege, psycopg.errors.CheckViolation, psycopg.errors.RaiseException)):
                    with connection.transaction():
                        cursor.execute(
                            """
                            INSERT INTO public.civic_cases
                            (case_id, case_type, subject, narrative, created_by, status, created_at, updated_at)
                            VALUES (%s, 'complaint', 'forged', 'forged', %s, 'draft', now(), now())
                            """,
                            ("rls-forged-" + uuid4().hex, "principal-a"),
                        )

                cursor.execute(
                    "UPDATE public.civic_cases SET subject = 'B must not mutate A' WHERE case_id = %s",
                    (case_id,),
                )
                assert cursor.rowcount == 0

                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with connection.transaction():
                        cursor.execute(
                            """
                            INSERT INTO public.civic_case_consents
                            (consent_id, case_id, purpose, scope, status, subject_id, created_at)
                            VALUES (%s, %s, 'forged', '{}'::jsonb, 'active', %s, now())
                            """,
                            ("forged-" + uuid4().hex, case_id, "principal-a"),
                        )

                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with connection.transaction():
                        cursor.execute(
                            """
                            INSERT INTO public.civic_case_submissions
                            (submission_id, case_id, destination_ref, channel, state, idempotency_key, created_at, updated_at)
                            VALUES (%s, %s, 'forged', 'test', 'pending', %s, now(), now())
                            """,
                            ("forged-" + uuid4().hex, case_id, "forged-idempotency-" + uuid4().hex),
                        )

                cursor.execute("SELECT set_config('janavani.principal_id', %s, true)", ("principal-a",))
                cursor.execute("UPDATE public.civic_cases SET subject = 'A can mutate A' WHERE case_id = %s", (case_id,))
                assert cursor.rowcount == 1

                cursor.execute("RESET ROLE")
                cursor.execute(
                    sql.SQL("REVOKE ALL PRIVILEGES ON SCHEMA public FROM {}").format(
                        sql.Identifier(role)
                    )
                )
                for table in (
                    "civic_cases",
                    "civic_case_consents",
                    "civic_case_submissions",
                    "civic_case_evidence_refs",
                    "civic_case_document_refs",
                    "evidence_objects",
                    "document_artifacts",
                ):
                    cursor.execute(
                        sql.SQL("REVOKE ALL PRIVILEGES ON public.{} FROM {}").format(
                            sql.Identifier(table), sql.Identifier(role)
                        )
                    )
                cursor.execute("DROP OWNED BY janavani_identity_service")
                cursor.execute("DROP ROLE janavani_identity_service")
                cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
