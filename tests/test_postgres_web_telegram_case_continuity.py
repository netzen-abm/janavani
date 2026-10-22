"""Live PostgreSQL proof that Web and Telegram share owner-scoped Case metadata."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.adapters.telegram.identity import identity_for_telegram_user
from src.commands.shared_case_capability import create_case_from_telegram
from src.core.civic_case import CaseType
from src.identity.external import ExternalIdentity
from src.identity.linking import PostgresExternalIdentityLinkRepository
from src.platform.surface_case_composition import create_surface_case_composition
from src.storage.repositories.postgres_civic_case import PostgresCivicCaseRepository
from src.web import civic_case_router
from src.web.canonical_app import app

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
pytestmark = pytest.mark.integration


def _auth_header(secret: str, principal_id: str) -> dict[str, str]:
    import time

    now = int(time.time())
    payload = {
        "iss": "janavani-identity",
        "aud": "janavani-api",
        "sub": principal_id,
        "provider": "test-identity",
        "subject": principal_id,
        "principal_id": principal_id,
        "authentication_method": "passkey",
        "iat": now,
        "exp": now + 60,
        "jti": f"cross-surface-{principal_id}-{uuid4().hex}",
        "capabilities": ["JNV-CIVIC-COMPLAINT", "case:read", "case:write", "case:review", "case:evidence"],
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    signature = hmac.new(secret.encode(), encoded.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return {"Authorization": f"Bearer {encoded}.{signed}"}


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_web_and_telegram_share_postgres_case_and_verified_principal(monkeypatch):
    import psycopg

    secret = "test-cross-surface-" + uuid4().hex
    principal_id = "citizen-" + uuid4().hex
    telegram_user_id = 700_000_000 + int(uuid4().hex[:7], 16)
    telegram_subject = str(telegram_user_id)
    schema = (ROOT / "db/migrations/20260912100000_canonical_case_policy_schema.sql").read_text()
    identity_schema = (ROOT / "db/migrations/20260920100000_external_identity_links.sql").read_text()
    with psycopg.connect(DSN) as connection:
        connection.execute(schema)
        connection.execute(identity_schema)

    case_repository = PostgresCivicCaseRepository(dsn=DSN)
    links = PostgresExternalIdentityLinkRepository(lambda: psycopg.connect(DSN))
    links.save(ExternalIdentity(
        provider="telegram",
        subject=telegram_subject,
        principal_id=principal_id,
        authentication_method="explicit_verified_link",
        verified=True,
        capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:read", "case:write", "case:review", "case:evidence"}),
    ))
    telegram_identity = identity_for_telegram_user(telegram_user_id, links=links)
    composition = create_surface_case_composition(
        case_repository=case_repository,
        identity_link_repository=links,
    )

    monkeypatch.setenv("JANAVANI_IDENTITY_ASSERTION_SECRET", secret)
    monkeypatch.setattr(civic_case_router, "_CAPABILITY", composition.case_capability)
    web_headers = _auth_header(secret, principal_id)
    other_headers = _auth_header(secret, "citizen-other-" + uuid4().hex)
    case_ids: list[str] = []

    try:
        with TestClient(app) as client:
            # Web creates a Case through the HTTP adapter and the shared capability.
            created = client.post(
                "/civic/cases",
                headers=web_headers,
                json={
                    "case_type": "complaint",
                    "subject": "Streetlight outage",
                    "narrative": "Sensitive details stay outside durable Case metadata.",
                },
            )
            assert created.status_code == 200, created.text
            web_case_id = created.json()["case_id"]
            case_ids.append(web_case_id)

            # The verified Telegram identity resolves to the same canonical principal,
            # which can read the Web-created Case through the same shared capability.
            seen_by_telegram = composition.case_capability.get_owned(
                web_case_id, identity=telegram_identity
            )
            assert seen_by_telegram is not None
            assert seen_by_telegram.created_by == principal_id
            assert seen_by_telegram.case_id == web_case_id

            # Telegram creates a Case shell through the canonical Telegram adapter.
            telegram_case = create_case_from_telegram(
                case_repository,
                identity=telegram_identity,
                subject="Water leak",
                narrative="Sensitive Telegram message is not persisted in Case metadata.",
                case_capability=composition.case_capability,
                case_type=CaseType.COMPLAINT,
            )
            telegram_case_id = telegram_case.case_id
            case_ids.append(telegram_case_id)

            # Web retrieves the Telegram-created Case from a fresh repository read.
            visible_to_web = client.get(f"/civic/cases/{telegram_case_id}", headers=web_headers)
            assert visible_to_web.status_code == 200, visible_to_web.text
            assert visible_to_web.json()["case_id"] == telegram_case_id
            assert visible_to_web.json()["created_by"] == principal_id
            assert any(
                event["source_channel"] == "telegram"
                for event in visible_to_web.json()["events"]
            )

            # Durable metadata keeps citizen narrative redacted; ownership remains enforced.
            for case_id in case_ids:
                with psycopg.connect(DSN) as connection:
                    row = connection.execute(
                        "SELECT subject, narrative, created_by FROM public.civic_cases WHERE case_id = %s",
                        (case_id,),
                    ).fetchone()
                assert row is not None
                assert row[0] == CaseType.COMPLAINT.value
                assert row[1] == ""
                assert row[2] == principal_id
            denied = client.get(f"/civic/cases/{telegram_case_id}", headers=other_headers)
            assert denied.status_code == 404
    finally:
        with psycopg.connect(DSN) as connection:
            with connection.transaction():
                for case_id in case_ids:
                    connection.execute("DELETE FROM public.civic_case_events WHERE case_id = %s", (case_id,))
                    connection.execute("DELETE FROM public.civic_cases WHERE case_id = %s", (case_id,))
                connection.execute(
                    "DELETE FROM public.external_identity_links WHERE provider = 'telegram' AND subject = %s",
                    (telegram_subject,),
                )
