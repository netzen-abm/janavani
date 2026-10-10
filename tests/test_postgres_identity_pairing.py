"""Live PostgreSQL pairing contract tests.

These tests use only JANAVANI_POSTGRES_TEST_DSN and refuse production-like DSNs.
They exercise independent repository instances to model separate Web/bot processes.
"""
from __future__ import annotations

import os
import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def _dsn() -> str:
    value = os.getenv("JANAVANI_POSTGRES_TEST_DSN", "").strip()
    if not value:
        pytest.skip("JANAVANI_POSTGRES_TEST_DSN is not configured")
    lowered = value.lower()
    if "test" not in lowered and "localhost" not in lowered and "127.0.0.1" not in lowered:
        pytest.fail("Refusing live pairing integration tests: DSN must clearly identify a test/local database")
    if os.getenv("JANAVANI_RUNTIME_MODE", "development").strip().lower() == "production":
        pytest.fail("Refusing to run pairing integration tests in production runtime mode")
    return value


@pytest.fixture()
def pairing_db():
    psycopg = pytest.importorskip("psycopg")
    dsn = _dsn()
    root = Path(__file__).resolve().parents[1]
    migrations = (
        root / "db/migrations/20260920100000_external_identity_links.sql",
        root / "db/migrations/20261010120000_external_identity_pairings.sql",
    )
    with psycopg.connect(dsn) as conn, conn.transaction(), conn.cursor() as cur:
        for migration in migrations:
            cur.execute(migration.read_text(encoding="utf-8"))
    yield dsn


def _repositories(dsn):
    from src.identity.pairing import IdentityPairingService
    from src.storage.repositories.postgres_identity_pairing import PostgresPairingRepository

    # Deliberately create distinct repository/service objects to simulate
    # separate processes sharing only PostgreSQL.
    return IdentityPairingService(PostgresPairingRepository(dsn=dsn))


def _cleanup(dsn, pairing_ids, subjects):
    import psycopg

    with psycopg.connect(dsn) as conn, conn.transaction(), conn.cursor() as cur:
        if pairing_ids:
            cur.execute(
                "DELETE FROM public.external_identity_pairings WHERE pairing_id = ANY(%s)",
                (pairing_ids,),
            )
        if subjects:
            cur.execute(
                "DELETE FROM public.external_identity_links WHERE provider = 'telegram' AND subject = ANY(%s)",
                (subjects,),
            )


def test_postgres_pairing_is_visible_across_independent_service_instances(pairing_db):
    dsn = pairing_db
    issuer, bot, confirmer = (_repositories(dsn) for _ in range(3))
    challenge = issuer.issue(principal_id=f"citizen:integration:{secrets.token_hex(8)}")
    try:
        claim = bot.claim_telegram(challenge.code, telegram_subject=f"test:{secrets.token_hex(12)}")
        identity = confirmer.confirm_from_web(
            challenge.pairing_id,
            principal_id=claim.principal_id,
            explicit_confirmation=True,
        )
        resolved = _repositories(dsn)
        from src.identity.linking import IdentityLinkResolver
        # A new repository instance must resolve the persisted verified link.
        from src.platform.composition_repositories import create_identity_link_repository
        from src.storage.provider_composition import ProviderComposition

        composition = ProviderComposition.memory_first().with_provider("external_identity_links", "postgres")
        links = create_identity_link_repository(provider_composition=composition)
        assert IdentityLinkResolver(links).resolve("telegram", identity.subject).principal_id == claim.principal_id
        with pytest.raises(LookupError):
            resolved.claim_telegram(challenge.code, telegram_subject=f"replay:{secrets.token_hex(8)}")
    finally:
        _cleanup(dsn, [challenge.pairing_id], [claim.subject] if "claim" in locals() else [])


def test_postgres_pairing_claim_has_exactly_one_winner_under_concurrency(pairing_db):
    dsn = pairing_db
    issuer = _repositories(dsn)
    challenge = issuer.issue(principal_id=f"citizen:race:{secrets.token_hex(8)}")
    subjects = [f"race:{secrets.token_hex(10)}" for _ in range(8)]

    def attempt(subject):
        try:
            return _repositories(dsn).claim_telegram(challenge.code, telegram_subject=subject)
        except (LookupError, ValueError):
            return None

    try:
        with ThreadPoolExecutor(max_workers=len(subjects)) as pool:
            results = list(pool.map(attempt, subjects))
        winners = [result for result in results if result is not None]
        assert len(winners) == 1
        assert winners[0].subject in subjects
    finally:
        _cleanup(dsn, [challenge.pairing_id], subjects)


def test_postgres_pairing_refuses_identity_reassignment(pairing_db):
    dsn = pairing_db
    first, second = _repositories(dsn), _repositories(dsn)
    subject = f"conflict:{secrets.token_hex(12)}"
    principal_one = f"citizen:one:{secrets.token_hex(8)}"
    principal_two = f"citizen:two:{secrets.token_hex(8)}"
    challenge_one = first.issue(principal_id=principal_one)
    challenge_two = second.issue(principal_id=principal_two)
    try:
        first.claim_telegram(challenge_one.code, telegram_subject=subject)
        first.confirm_from_web(
            challenge_one.pairing_id, principal_id=principal_one, explicit_confirmation=True,
        )
        second.claim_telegram(challenge_two.code, telegram_subject=subject)
        with pytest.raises(PermissionError):
            second.confirm_from_web(
                challenge_two.pairing_id, principal_id=principal_two, explicit_confirmation=True,
            )
        from src.identity.linking import IdentityLinkResolver
        from src.platform.composition_repositories import create_identity_link_repository
        from src.storage.provider_composition import ProviderComposition

        composition = ProviderComposition.memory_first().with_provider("external_identity_links", "postgres")
        resolved = IdentityLinkResolver(create_identity_link_repository(provider_composition=composition))
        assert resolved.resolve("telegram", subject).principal_id == principal_one
    finally:
        _cleanup(dsn, [challenge_one.pairing_id, challenge_two.pairing_id], [subject])
