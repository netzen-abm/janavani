from datetime import datetime, timedelta, timezone

import pytest

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
