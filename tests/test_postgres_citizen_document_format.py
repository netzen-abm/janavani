"""Live PostgreSQL acceptance for owner-scoped saved-format persistence."""
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest

DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN", "").strip()
ROOT = Path(__file__).parents[1]
MIGRATION = ROOT / "db/migrations/20261030120000_citizen_document_formats.sql"


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_saved_formats_enforce_owner_scope_and_survive_repository_restart():
    import psycopg
    from psycopg import sql
    from psycopg.conninfo import make_conninfo

    runtime_dsns = {
        os.getenv(name, "").strip()
        for name in (
            "JANAVANI_POSTGRES_DSN",
            "JANAVANI_IDENTITY_LINKS_DSN",
            "JANAVANI_CASE_DATABASE_URL",
            "JANAVANI_CITIZEN_DOCUMENT_FORMAT_DSN",
        )
    } - {""}
    assert DSN not in runtime_dsns, "the integration DSN must not be a configured runtime database"
    assert any(token in DSN.lower() for token in ("test", "localhost", "127.0.0.1")), (
        "the saved-format integration test requires a clearly identified disposable test database"
    )

    owner_a = f"synthetic-owner-a-{uuid4().hex}"
    owner_b = f"synthetic-owner-b-{uuid4().hex}"
    role = f"jnv_fmt_{uuid4().hex[:12]}"
    password = f"test-password-{uuid4().hex}"
    role_created = False

    try:
        with psycopg.connect(DSN) as admin:
            admin.execute(MIGRATION.read_text(encoding="utf-8"))
            admin.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB "
                    "NOCREATEROLE NOINHERIT NOBYPASSRLS"
                ).format(sql.Identifier(role), sql.Literal(password))
            )
            admin.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                    sql.Identifier(admin.info.dbname), sql.Identifier(role)
                )
            )
            admin.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(role)))
            admin.execute(
                sql.SQL(
                    "GRANT SELECT, INSERT, UPDATE, DELETE "
                    "ON TABLE public.citizen_document_formats TO {}"
                ).format(sql.Identifier(role))
            )
            role_created = True
            flags = admin.execute(
                "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = %s",
                (role,),
            ).fetchone()
            assert flags == (False, False), "test runtime role must not bypass RLS"

        role_dsn = make_conninfo(
            DSN,
            user=role,
            password=password,
            application_name="janavani-saved-format-rls-test",
        )
        from src.documents.citizen_document_format import create_citizen_document_format
        from src.storage.repositories.postgres_citizen_document_format import (
            PostgresCitizenDocumentFormatRepository,
        )

        repository = PostgresCitizenDocumentFormatRepository(dsn=role_dsn)
        first_candidate = create_citizen_document_format(
            owner_principal_id=owner_a,
            template_id="complaint.general",
            template_version=1,
            section_field_names=["issue", "proposal_or_notice"],
        )
        first = repository.save(first_candidate, owner_principal_id=owner_a)
        duplicate = repository.save(
            create_citizen_document_format(
                owner_principal_id=owner_a,
                template_id="complaint.general",
                template_version=1,
                section_field_names=["proposal_or_notice", "issue"],
            ),
            owner_principal_id=owner_a,
        )
        assert duplicate.format_id == first.format_id
        assert repository.get_for_owner(first.format_id, owner_principal_id=owner_a) == first
        assert [row.format_id for row in repository.list_for_owner(owner_principal_id=owner_a)] == [
            first.format_id
        ]

        # A separate connection using a non-superuser, NOBYPASSRLS role proves that
        # PostgreSQL RLS—not only Python owner predicates—hides the other owner's row.
        with psycopg.connect(role_dsn) as limited:
            with limited.transaction():
                limited.execute(
                    "SELECT set_config('janavani.principal_id', %s, true)", (owner_b,)
                )
                visible = limited.execute(
                    "SELECT count(*) FROM public.citizen_document_formats WHERE format_id = %s",
                    (first.format_id,),
                ).fetchone()[0]
                assert visible == 0

        assert repository.get_for_owner(first.format_id, owner_principal_id=owner_b) is None
        assert repository.list_for_owner(owner_principal_id=owner_b) == []
        assert repository.delete_for_owner(first.format_id, owner_principal_id=owner_b) is False

        second_owner = repository.save(
            create_citizen_document_format(
                owner_principal_id=owner_b,
                template_id="complaint.general",
                template_version=1,
                section_field_names=["issue", "proposal_or_notice"],
            ),
            owner_principal_id=owner_b,
        )
        assert second_owner.format_id != first.format_id

        # Recreate the repository to prove database durability independent of an
        # in-process map or the original repository instance.
        restarted_repository = PostgresCitizenDocumentFormatRepository(dsn=role_dsn)
        recovered = restarted_repository.get_for_owner(
            first.format_id, owner_principal_id=owner_a
        )
        assert recovered is not None
        assert recovered.structure_hash == first.structure_hash
        assert recovered.section_field_names == first.section_field_names
        assert restarted_repository.delete_for_owner(
            first.format_id, owner_principal_id=owner_a
        ) is True
        assert restarted_repository.get_for_owner(
            first.format_id, owner_principal_id=owner_a
        ) is None

        with psycopg.connect(DSN) as admin:
            columns = {
                row[0]
                for row in admin.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = 'citizen_document_formats'"
                ).fetchall()
            }
        assert not columns.intersection(
            {"narrative", "source_draft", "document_body", "evidence_content"}
        )
    finally:
        if role_created:
            with psycopg.connect(DSN) as admin:
                admin.execute(
                    "DELETE FROM public.citizen_document_formats "
                    "WHERE owner_principal_id IN (%s, %s)",
                    (owner_a, owner_b),
                )
                admin.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(role)))
                admin.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role)))
