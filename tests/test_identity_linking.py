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
        subject="telegram-subject-1", authentication_method="oidc"), verified=True)
    with pytest.raises(PermissionError):
        service.link_verified(IdentityLinkRequest(
            principal_id="janavani:opaque-2", provider="telegram",
            subject="telegram-subject-1", authentication_method="oidc"), verified=True)


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


def test_production_postgres_identity_provider_requires_dedicated_dsn(monkeypatch):
    from src.platform.composition_repositories import create_identity_link_repository
    from src.storage.provider_composition import ProviderComposition

    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")
    monkeypatch.setenv("JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER", "postgres")
    monkeypatch.setenv("JANAVANI_POSTGRES_DSN", "postgresql://shared-role.invalid/db")
    monkeypatch.delenv("JANAVANI_IDENTITY_LINKS_DSN", raising=False)

    with pytest.raises(ValueError, match="JANAVANI_IDENTITY_LINKS_DSN is required in production"):
        create_identity_link_repository(
            provider_composition=ProviderComposition.memory_first().with_provider(
                "external_identity_links", "postgres"
            )
        )


def test_production_postgres_identity_provider_accepts_dedicated_dsn(monkeypatch):
    from src.platform.composition_repositories import create_identity_link_repository
    from src.identity.linking import PostgresExternalIdentityLinkRepository
    from src.storage.provider_composition import ProviderComposition

    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")
    monkeypatch.setenv("JANAVANI_IDENTITY_LINKS_DSN", "postgresql://identity-role.invalid/db")
    monkeypatch.setenv("JANAVANI_POSTGRES_DSN", "postgresql://shared-role.invalid/db")

    repository = create_identity_link_repository(
        provider_composition=ProviderComposition.memory_first().with_provider(
            "external_identity_links", "postgres"
        )
    )
    assert isinstance(repository, PostgresExternalIdentityLinkRepository)
