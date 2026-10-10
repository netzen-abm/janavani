"""Opt-in PostgreSQL integration tests for cross-process identity pairing.

Set JANAVANI_POSTGRES_TEST_DSN to a dedicated disposable test database whose
public schema has the identity-link and pairing migrations applied. The tests
never create/drop shared tables; they use unique test principals and clean up
only rows they create.
"""
from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from src.identity.pairing import IdentityPairingService
from src.storage.repositories.postgres_identity_pairing import PostgresPairingRepository


@pytest.fixture
def postgres_pairing():
    dsn = os.getenv("JANAVANI_POSTGRES_TEST_DSN", "").strip()
    if not dsn:
        pytest.skip("Set JANAVANI_POSTGRES_TEST_DSN to run PostgreSQL pairing integration tests")
    if os.getenv("JANAVANI_RUNTIME_MODE", "development").strip().lower() == "production":
        pytest.fail("PostgreSQL pairing integration tests must never run in production mode")
    runtime_dsns = {
        os.getenv("JANAVANI_IDENTITY_LINKS_DSN", "").strip(),
        os.getenv("JANAVANI_POSTGRES_DSN", "").strip(),
    } - {""}
    if dsn in runtime_dsns:
        pytest.fail("JANAVANI_POSTGRES_TEST_DSN must be a dedicated database, not a runtime DSN")

    psycopg = pytest.importorskip("psycopg")
    suffix = uuid.uuid4().hex
    principal_id = f"test:pairing:{suffix}"
    subject_prefix = f"test:telegram:{suffix}:"
    repository = PostgresPairingRepository(dsn=dsn)

    # Apply migrations only to the explicitly configured dedicated test database.
    # The fixture above refuses production mode and runtime DSNs.
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    migrations = (
        repo_root / "db/migrations/20260920100000_external_identity_links.sql",
        repo_root / "db/migrations/20261010120000_external_identity_pairings.sql",
    )
    with psycopg.connect(dsn) as conn, conn.transaction(), conn.cursor() as cur:
        for migration in migrations:
            cur.execute(migration.read_text(encoding="utf-8"))
        cur.execute(
            "SELECT to_regclass('public.external_identity_pairings'), "
            "to_regclass('public.external_identity_links')"
        )
        tables = cur.fetchone()
        assert tables == ("external_identity_pairings", "external_identity_links"), (
            "Identity pairing migrations did not create the required test tables"
        )

    yield {
        "dsn": dsn,
        "principal_id": principal_id,
        "subject_prefix": subject_prefix,
        "repository": repository,
        "service": IdentityPairingService(repository),
        "new_service": lambda: IdentityPairingService(PostgresPairingRepository(dsn=dsn)),
    }

    with psycopg.connect(dsn) as conn, conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "DELETE FROM public.external_identity_pairings WHERE principal_id = %s",
            (principal_id,),
        )
        cur.execute(
            "DELETE FROM public.external_identity_links WHERE subject LIKE %s",
            (subject_prefix + "%",),
        )


@pytest.mark.integration
def test_postgres_pairing_is_visible_across_independent_repository_instances(postgres_pairing):
    state = postgres_pairing
    now = datetime.now(timezone.utc)
    challenge = state["service"].issue(principal_id=state["principal_id"], now=now)

    # Simulate the Telegram worker running in a separate process with its own repository.
    telegram_service = state["new_service"]()
    claim = telegram_service.claim_telegram(
        challenge.code, telegram_subject=state["subject_prefix"] + "shared", now=now,
    )
    assert claim.principal_id == state["principal_id"]

    # A fresh Web-side repository instance confirms and commits the link.
    web_service = state["new_service"]()
    identity = web_service.confirm_from_web(
        challenge.pairing_id, principal_id=state["principal_id"],
        explicit_confirmation=True, now=now,
    )
    assert identity.verified is True

    # Another fresh instance sees the committed identity mapping.
    with __import__("psycopg").connect(state["dsn"]) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT principal_id, verified FROM public.external_identity_links WHERE provider = 'telegram' AND subject = %s",
            (identity.subject,),
        )
        assert cur.fetchone() == (state["principal_id"], True)


@pytest.mark.integration
def test_postgres_pairing_claim_is_single_use_under_concurrency(postgres_pairing):
    state = postgres_pairing
    now = datetime.now(timezone.utc)
    challenge = state["service"].issue(principal_id=state["principal_id"], now=now)

    def claim(subject: str) -> str:
        service = state["new_service"]()
        try:
            service.claim_telegram(challenge.code, telegram_subject=subject, now=now)
            return "claimed"
        except LookupError:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(
            claim,
            [state["subject_prefix"] + "race-a", state["subject_prefix"] + "race-b"],
        ))
    assert sorted(outcomes) == ["claimed", "rejected"]


@pytest.mark.integration
def test_postgres_pairing_conflict_rolls_back_confirmation(postgres_pairing):
    state = postgres_pairing
    now = datetime.now(timezone.utc)
    subject = state["subject_prefix"] + "already-linked"
    challenge = state["service"].issue(principal_id=state["principal_id"], now=now)
    state["service"].claim_telegram(challenge.code, telegram_subject=subject, now=now)

    with __import__("psycopg").connect(state["dsn"]) as conn, conn.transaction(), conn.cursor() as cur:
        cur.execute(
            """INSERT INTO public.external_identity_links
               (provider, subject, principal_id, authentication_method, verified)
               VALUES ('telegram', %s, %s, 'test_fixture', true)""",
            (subject, state["principal_id"] + ":different"),
        )

    with pytest.raises(PermissionError, match="already linked"):
        state["service"].confirm_from_web(
            challenge.pairing_id, principal_id=state["principal_id"],
            explicit_confirmation=True, now=now,
        )

    with __import__("psycopg").connect(state["dsn"]) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT confirmed_at FROM public.external_identity_pairings WHERE pairing_id = %s",
            (challenge.pairing_id,),
        )
        assert cur.fetchone() == (None,)


@pytest.mark.integration
def test_postgres_pairing_rejects_expired_code(postgres_pairing):
    state = postgres_pairing
    now = datetime.now(timezone.utc)
    challenge = state["service"].issue(
        principal_id=state["principal_id"], now=now - timedelta(minutes=6),
    )
    with pytest.raises(LookupError, match="invalid, expired"):
        state["new_service"]().claim_telegram(
            challenge.code, telegram_subject=state["subject_prefix"] + "expired", now=now,
        )
