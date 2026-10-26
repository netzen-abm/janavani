"""PostgreSQL integration proof for identity-pairing least-privilege migration."""
from __future__ import annotations
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
MIGRATION = ROOT / "db/migrations/20261026130000_revoke_excess_external_identity_pairing_privileges.sql"
FORBIDDEN = ("TRUNCATE", "REFERENCES", "TRIGGER")
ROLES = ("anon", "authenticated", "service_role")

@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_pairing_privilege_migration_revokes_structural_grants():
    import psycopg

    runtime_dsns = {
        os.getenv(name, "").strip()
        for name in ("JANAVANI_POSTGRES_DSN", "JANAVANI_IDENTITY_LINKS_DSN", "JANAVANI_CASE_DATABASE_URL")
    } - {""}
    assert DSN not in runtime_dsns, "test DSN must not be a runtime database"
    assert any(value in DSN.lower() for value in ("test", "localhost", "127.0.0.1"))
    assert os.getenv("JANAVANI_RUNTIME_MODE", "test").lower() != "production"

    with psycopg.connect(DSN) as connection:
        connection.execute((ROOT / "db/migrations/20260920100000_external_identity_links.sql").read_text())
        connection.execute((ROOT / "db/migrations/20261010120000_external_identity_pairings.sql").read_text())
        connection.execute("""
            DO $roles$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    CREATE ROLE anon NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    CREATE ROLE authenticated NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
                    CREATE ROLE service_role NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
                END IF;
            END
            $roles$;
        """)
        connection.execute(
            "GRANT TRUNCATE, REFERENCES, TRIGGER ON TABLE public.external_identity_pairings "
            "TO PUBLIC, anon, authenticated, service_role"
        )
        for role in ROLES:
            for privilege in FORBIDDEN:
                assert connection.execute(
                    "SELECT has_table_privilege(%s, 'public.external_identity_pairings', %s)",
                    (role, privilege),
                ).fetchone()[0], f"fixture did not seed {role}:{privilege}"

        migration_sql = MIGRATION.read_text(encoding="utf-8")
        connection.execute(migration_sql)
        connection.execute(migration_sql)  # Reapplying REVOKE is intentionally safe.
        remaining = connection.execute("""
            SELECT grantee, privilege_type
            FROM information_schema.role_table_grants
            WHERE table_schema = 'public'
              AND table_name = 'external_identity_pairings'
              AND grantee IN ('PUBLIC', 'anon', 'authenticated', 'service_role')
              AND privilege_type = ANY(%s)
            ORDER BY grantee, privilege_type
        """, (list(FORBIDDEN),)).fetchall()
        assert remaining == [], f"excess pairing-table grants remain: {remaining}"
