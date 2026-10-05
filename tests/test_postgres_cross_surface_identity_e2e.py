from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.capabilities.civic_case import CAPABILITY_ID, CivicCaseCreateRequest
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.linking import IdentityLinkRequest, IdentityLinkingService, IdentityLinkResolver
from src.identity.principal import IdentityMode, Principal
from src.platform.surface_case_composition import create_surface_case_composition
from src.storage.provider_composition import ProviderComposition

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")

pytestmark = pytest.mark.integration


def _schema() -> None:
    psycopg = pytest.importorskip("psycopg")
    base = (ROOT / "db/migrations/20260912100000_canonical_case_policy_schema.sql").read_text(
        encoding="utf-8"
    )
    identity = (ROOT / "db/migrations/20260920100000_external_identity_links.sql").read_text(
        encoding="utf-8"
    )
    with psycopg.connect(DSN) as connection:
        connection.execute(base)
        connection.execute(identity)


def _identity(principal_id: str, interface: str) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            interface=interface,
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )


@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_web_and_telegram_share_durable_identity_and_case_state():
    _schema()

    providers = (
        ProviderComposition.memory_first()
        .with_provider("civic_case", "postgres")
        .with_provider("external_identity_links", "postgres")
    )

    telegram = create_surface_case_composition(provider_composition=providers)
    web = create_surface_case_composition(provider_composition=providers)

    principal_id = "janavani:e2e-principal"
    links = telegram.identity_link_repository
    IdentityLinkingService(links).link_verified(
        IdentityLinkRequest(
            principal_id=principal_id,
            provider="telegram",
            subject="e2e-telegram-user",
            authentication_method="explicit_verified_link",
        ),
        verified=True,
    )

    linked = links.find("telegram", "e2e-telegram-user")
    assert linked is not None
    assert linked.principal_id == principal_id
    assert linked.verified is True
    resolved = IdentityLinkResolver(links).resolve("telegram", "e2e-telegram-user")
    assert resolved.principal_id == principal_id

    created = telegram.case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Durable cross-surface Case",
            narrative="Created through Telegram and read through Web.",
        ),
        identity=_identity(principal_id, "telegram"),
        source_channel="telegram",
    )
    case_id = created.case.case_id

    fresh_web = create_surface_case_composition(provider_composition=providers)
    fresh_telegram = create_surface_case_composition(provider_composition=providers)

    assert fresh_web.case_capability is not fresh_telegram.case_capability
    assert fresh_web.case_repository is fresh_telegram.case_repository
    assert fresh_web.identity_link_repository is fresh_telegram.identity_link_repository

    web_case = fresh_web.case_capability.get_owned(
        case_id, identity=_identity(principal_id, "webapp")
    )
    telegram_case = fresh_telegram.case_capability.get_owned(
        case_id, identity=_identity(principal_id, "telegram")
    )

    assert web_case is not None
    assert telegram_case is not None
    assert web_case.case_id == telegram_case.case_id == case_id
    assert web_case.created_by == principal_id
    assert telegram_case.created_by == principal_id

    stranger = _identity("janavani:e2e-stranger", "webapp")
    assert fresh_web.case_capability.get_owned(case_id, identity=stranger) is None
