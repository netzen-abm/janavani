from datetime import datetime, timedelta, timezone

import pytest

from src.identity.linking import IdentityLinkRequest, IdentityLinkResolver, InMemoryExternalIdentityLinkRepository, IdentityLinkingService
from src.identity.pairing import IdentityPairingService, InMemoryPairingRepository


NOW = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)


def setup_pairing():
    repository = InMemoryPairingRepository()
    service = IdentityPairingService(repository)
    return repository, service


def test_pairing_requires_claim_and_explicit_web_confirmation():
    repository, service = setup_pairing()
    challenge = service.issue(principal_id="citizen:one", now=NOW)

    with pytest.raises(LookupError):
        service.confirm_from_web(challenge.pairing_id, principal_id="citizen:one",
                                 explicit_confirmation=True, now=NOW)

    claim = service.claim_telegram(challenge.code, telegram_subject="tg:123", now=NOW)
    assert claim.principal_id == "citizen:one"
    with pytest.raises(PermissionError):
        service.confirm_from_web(challenge.pairing_id, principal_id="citizen:one",
                                 explicit_confirmation=False, now=NOW)

    identity = service.confirm_from_web(challenge.pairing_id, principal_id="citizen:one",
                                        explicit_confirmation=True, now=NOW)
    assert identity.provider == "telegram"
    assert identity.subject == "tg:123"
    assert identity.principal_id == "citizen:one"
    assert identity.verified is True
    assert identity.authentication_method == "web_telegram_pairing"


def test_pairing_code_is_single_use_and_cannot_be_confirmed_by_another_principal():
    _, service = setup_pairing()
    challenge = service.issue(principal_id="citizen:one", now=NOW)
    service.claim_telegram(challenge.code, telegram_subject="tg:123", now=NOW)

    with pytest.raises(LookupError):
        service.claim_telegram(challenge.code, telegram_subject="tg:attacker", now=NOW)
    with pytest.raises(LookupError):
        service.confirm_from_web(challenge.pairing_id, principal_id="citizen:other",
                                 explicit_confirmation=True, now=NOW)

    service.confirm_from_web(challenge.pairing_id, principal_id="citizen:one",
                             explicit_confirmation=True, now=NOW)
    with pytest.raises(LookupError):
        service.confirm_from_web(challenge.pairing_id, principal_id="citizen:one",
                                 explicit_confirmation=True, now=NOW)


def test_pairing_expiry_and_timezone_requirements():
    _, service = setup_pairing()
    challenge = service.issue(principal_id="citizen:one", now=NOW)
    with pytest.raises(LookupError):
        service.claim_telegram(challenge.code, telegram_subject="tg:123",
                               now=NOW + timedelta(minutes=6))
    with pytest.raises(ValueError, match="timezone-aware"):
        service.issue(principal_id="citizen:one", now=datetime(2026, 10, 10, 12, 0))


def test_pairing_rejects_empty_principal_and_telegram_subject():
    _, service = setup_pairing()
    with pytest.raises(ValueError):
        service.issue(principal_id=" ")
    challenge = service.issue(principal_id="citizen:one", now=NOW)
    with pytest.raises(ValueError):
        service.claim_telegram(challenge.code, telegram_subject=" ", now=NOW)


def test_pairing_persists_only_a_digest_and_never_exposes_code_in_repository_state():
    repository, service = setup_pairing()
    challenge = service.issue(principal_id="citizen:one", now=NOW)
    stored = repository._items[challenge.pairing_id]
    assert stored.token_digest != challenge.code
    assert len(stored.token_digest) == 64
    assert not hasattr(stored, "code")


def test_identity_resolver_accepts_only_the_confirmed_link():
    links = InMemoryExternalIdentityLinkRepository()
    _, service = setup_pairing()
    challenge = service.issue(principal_id="citizen:one", now=NOW)
    service.claim_telegram(challenge.code, telegram_subject="tg:123", now=NOW)
    identity = service.confirm_from_web(challenge.pairing_id, principal_id="citizen:one",
                                        explicit_confirmation=True, now=NOW)
    IdentityLinkingService(links).link_verified(
        IdentityLinkRequest(
            principal_id=identity.principal_id, provider=identity.provider, subject=identity.subject,
            authentication_method=identity.authentication_method,
        ),
        verified=identity.verified,
    )
    assert IdentityLinkResolver(links).resolve("telegram", "tg:123").principal_id == "citizen:one"
