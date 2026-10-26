from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.core.authority import AuthorityContact, AuthorityRecord
from src.storage.repositories.postgres_authority import PostgresAuthorityRepository


def _repository() -> tuple[PostgresAuthorityRepository, MagicMock, MagicMock]:
    connection = MagicMock()
    connection.__enter__.return_value = connection
    cursor = connection.cursor.return_value.__enter__.return_value
    connection.transaction.return_value.__enter__.return_value = connection
    repo = PostgresAuthorityRepository(connection_factory=lambda: connection)
    cursor.reset_mock()
    return repo, connection, cursor


def _record() -> AuthorityRecord:
    return AuthorityRecord(
        authority_id="office-1",
        name="District Officer",
        authority_type="district_officer",
        jurisdiction={"city": "Bengaluru", "district": "Bengaluru Urban"},
        primary_contact=AuthorityContact(
            name="District Officer",
            address="District Office",
            email="office@example.gov.in",
            role="District Officer",
            source_ref="official-directory",
            verified=True,
        ),
        cc_contacts=(AuthorityContact(name="Registry", address="Registry Office"),),
        source_refs=("official-directory",),
        verification_status="VERIFIED",
        last_verified_at="2026-09-10T00:00:00Z",
    )


def test_save_serializes_canonical_authority_contract() -> None:
    repo, _, cursor = _repository()

    repo.save(_record())

    sql, params = cursor.execute.call_args.args
    assert "INSERT INTO civic_authorities" in sql
    assert params[0] == "office-1"
    assert json.loads(params[3])["city"] == "Bengaluru"
    assert json.loads(params[4])["email"] == "office@example.gov.in"
    assert json.loads(params[5])[0]["name"] == "Registry"
    assert json.loads(params[6]) == ["official-directory"]
    assert params[7] == "VERIFIED"


def test_get_hydrates_authority_record() -> None:
    repo, _, cursor = _repository()
    cursor.fetchone.return_value = (
        "office-1",
        "District Officer",
        "district_officer",
        {"city": "Bengaluru"},
        {"name": "District Officer", "address": "District Office", "email": None, "role": None, "source_ref": None, "verified": True},
        [],
        ["official-directory"],
        "VERIFIED",
        "2026-09-10T00:00:00Z",
    )

    result = repo.get("office-1")

    assert result is not None
    assert result.authority_id == "office-1"
    assert result.jurisdiction["city"] == "Bengaluru"
    assert result.verified is True
    assert result.source_refs == ("official-directory",)


def test_search_uses_canonical_type_and_city_fields() -> None:
    repo, _, cursor = _repository()
    cursor.fetchall.return_value = []

    assert repo.search(authority_type="District Officer", city="Bengaluru", limit=3) == []

    sql, params = cursor.execute.call_args.args
    assert "authority_type" in sql
    assert "jurisdiction->>'city'" in sql
    assert params == ("%district officer%", "%bengaluru%", 3)


def test_search_rejects_non_positive_limit_without_query() -> None:
    repo, _, cursor = _repository()

    assert repo.search(authority_type="district", city="Bengaluru", limit=0) == []
    cursor.execute.assert_not_called()


def test_repository_construction_does_not_open_database_or_run_ddl() -> None:
    connection_factory = MagicMock()

    PostgresAuthorityRepository(connection_factory=connection_factory)

    connection_factory.assert_not_called()


ROOT = Path(__file__).resolve().parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
AUTHORITY_MIGRATION = ROOT / "db/migrations/20261026140000_create_civic_authorities.sql"


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_versioned_authority_migration_creates_table_and_index_idempotently():
    import psycopg

    runtime_dsns = {
        os.getenv(name, "").strip()
        for name in ("JANAVANI_POSTGRES_DSN", "JANAVANI_IDENTITY_LINKS_DSN", "JANAVANI_CASE_DATABASE_URL")
    } - {""}
    assert DSN not in runtime_dsns, "test DSN must not be a runtime database"
    assert any(value in DSN.lower() for value in ("test", "localhost", "127.0.0.1"))
    assert os.getenv("JANAVANI_RUNTIME_MODE", "test").lower() != "production"

    migration_sql = AUTHORITY_MIGRATION.read_text(encoding="utf-8")
    with psycopg.connect(DSN) as connection:
        connection.execute(migration_sql)
        connection.execute(migration_sql)
        columns = connection.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'civic_authorities'
            ORDER BY ordinal_position
        """).fetchall()
        index = connection.execute("""
            SELECT to_regclass('public.civic_authorities_type_city_idx')
        """).fetchone()[0]
    assert [row[0] for row in columns] == [
        "authority_id", "name", "authority_type", "jurisdiction",
        "primary_contact", "cc_contacts", "source_refs",
        "verification_status", "last_verified_at",
    ]
    assert index == "civic_authorities_type_city_idx"
