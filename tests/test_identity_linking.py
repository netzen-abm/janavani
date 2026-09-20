import pytest
from src.identity.linking import IdentityLinkRequest, IdentityLinkingService, InMemoryExternalIdentityLinkRepository

def test_verified_external_identity_can_be_linked_once():
    service = IdentityLinkingService(InMemoryExternalIdentityLinkRepository())
    identity = service.link_verified(IdentityLinkRequest(
        principal_id="janavani:opaque-1", provider="telegram",
        subject="telegram-subject-1", authentication_method="oidc"), verified=True)
    assert identity.principal_id == "janavani:opaque-1"
    assert identity.provider == "telegram"

def test_unverified_linking_fails_closed():
    service = IdentityLinkingService(InMemoryExternalIdentityLinkRepository())
    with pytest.raises(PermissionError):
        service.link_verified(IdentityLinkRequest(
            principal_id="janavani:opaque-1", provider="telegram",
            subject="telegram-subject-1", authentication_method="oidc"), verified=False)

def test_one_external_identity_cannot_be_linked_to_two_principals():
    service = IdentityLinkingService(InMemoryExternalIdentityLinkRepository())
    service.link_verified(IdentityLinkRequest(
        principal_id="janavani:opaque-1", provider="telegram",
        subject="telegram-subject-1", authentication_method="none"), verified=True)
    with pytest.raises(PermissionError):
        service.link_verified(IdentityLinkRequest(
            principal_id="janavani:opaque-2", provider="telegram",
            subject="telegram-subject-1", authentication_method="none"), verified=True)


def test_postgres_identity_repository_has_provider_neutral_contract():
    from src.identity.linking import ExternalIdentityLinkRepository, PostgresExternalIdentityLinkRepository
    assert isinstance(PostgresExternalIdentityLinkRepository, type)
    assert hasattr(ExternalIdentityLinkRepository, "find")
    assert hasattr(ExternalIdentityLinkRepository, "save")


def test_identity_link_schema_exists():
    from pathlib import Path
    migration = Path(__file__).parents[1] / "db/migrations/20260920100000_external_identity_links.sql"
    text = migration.read_text(encoding="utf-8")
    assert "external_identity_links" in text
    assert "PRIMARY KEY (provider, subject)" in text
