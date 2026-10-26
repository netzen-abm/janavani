from datetime import datetime, timedelta, timezone

import pytest

from src.identity.external import ExternalIdentity
from src.identity.linking import InMemoryExternalIdentityLinkRepository
from src.identity.pairing import IdentityPairingService, InMemoryPairingRepository


def test_pairing_cannot_be_confirmed_by_a_different_web_principal():
    service = IdentityPairingService(InMemoryPairingRepository())
    now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
    challenge = service.issue(principal_id="citizen:alice", now=now)
    service.claim_telegram(
        challenge.code,
        telegram_subject="telegram:123",
        now=now + timedelta(seconds=1),
    )

    with pytest.raises(LookupError):
        service.confirm_from_web(
            challenge.pairing_id,
            principal_id="citizen:bob",
            explicit_confirmation=True,
            now=now + timedelta(seconds=2),
        )


def test_pairing_cannot_be_confirmed_before_telegram_claim():
    service = IdentityPairingService(InMemoryPairingRepository())
    now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
    challenge = service.issue(principal_id="citizen:alice", now=now)

    with pytest.raises(LookupError):
        service.confirm_from_web(
            challenge.pairing_id,
            principal_id="citizen:alice",
            explicit_confirmation=True,
            now=now + timedelta(seconds=1),
        )


def test_pairing_code_cannot_be_claimed_after_expiry():
    service = IdentityPairingService(InMemoryPairingRepository())
    now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
    challenge = service.issue(principal_id="citizen:alice", now=now)

    with pytest.raises(LookupError, match="invalid, expired, or already used"):
        service.claim_telegram(
            challenge.code,
            telegram_subject="telegram:123",
            now=challenge.expires_at,
        )


def test_pairing_requires_explicit_confirmation():
    service = IdentityPairingService(InMemoryPairingRepository())
    now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
    challenge = service.issue(principal_id="citizen:alice", now=now)
    service.claim_telegram(
        challenge.code,
        telegram_subject="telegram:123",
        now=now + timedelta(seconds=1),
    )

    with pytest.raises(PermissionError, match="Explicit confirmation"):
        service.confirm_from_web(
            challenge.pairing_id,
            principal_id="citizen:alice",
            explicit_confirmation=False,
            now=now + timedelta(seconds=2),
        )


def test_in_memory_pairing_remains_unconfirmed_when_identity_link_conflicts():
    now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
    links = InMemoryExternalIdentityLinkRepository()
    links.save(ExternalIdentity(
        provider="telegram",
        subject="telegram:already-linked",
        principal_id="citizen:bob",
        authentication_method="web_telegram_pairing",
        verified=True,
    ))
    repository = InMemoryPairingRepository(identity_link_repository=links)
    service = IdentityPairingService(repository)
    challenge = service.issue(principal_id="citizen:alice", now=now)
    service.claim_telegram(
        challenge.code,
        telegram_subject="telegram:already-linked",
        now=now + timedelta(seconds=1),
    )

    with pytest.raises((PermissionError, ValueError)):
        service.confirm_from_web(
            challenge.pairing_id,
            principal_id="citizen:alice",
            explicit_confirmation=True,
            now=now + timedelta(seconds=2),
        )

    assert repository._items[challenge.pairing_id].confirmed_at is None
    assert links.find("telegram", "telegram:already-linked").principal_id == "citizen:bob"
