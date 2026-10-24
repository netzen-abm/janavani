import pytest

from src.adapters.telegram.identity import identity_for_telegram_user
from src.identity.external import ExternalIdentity
from src.identity.linking import InMemoryExternalIdentityLinkRepository


def test_telegram_identity_requires_verified_link():
    links = InMemoryExternalIdentityLinkRepository()

    with pytest.raises(LookupError):
        identity_for_telegram_user(12345, links=links)


def test_telegram_identity_resolves_to_linked_canonical_principal():
    links = InMemoryExternalIdentityLinkRepository()
    links.save(
        ExternalIdentity(
            provider="telegram",
            subject="12345",
            principal_id="janavani:principal-a",
            authentication_method="explicit_verified_link",
            verified=True,
        )
    )

    first = identity_for_telegram_user(12345, links=links)
    second = identity_for_telegram_user(12345, links=links)

    assert first.principal.principal_id == "janavani:principal-a"
    assert first.principal.principal_id == second.principal.principal_id
    assert "JNV-CIVIC-COMPLAINT" in first.principal.capabilities
    assert {"case:read", "case:write", "case:review", "case:evidence"} <= first.principal.capabilities
    assert not ({"admin:access", "service:execute", "destination:deliver"} & first.principal.capabilities)


def test_telegram_verified_link_receives_only_baseline_citizen_capabilities():
    links = InMemoryExternalIdentityLinkRepository()
    links.save(
        ExternalIdentity(
            provider="telegram",
            subject="12345",
            principal_id="janavani:principal-a",
            authentication_method="explicit_verified_link",
            verified=True,
            capabilities=frozenset({"admin:access", "service:execute"}),
        )
    )

    identity = identity_for_telegram_user(12345, links=links)

    assert "JNV-CIVIC-COMPLAINT" in identity.principal.capabilities
    assert not ({"admin:access", "service:execute"} & identity.principal.capabilities)
