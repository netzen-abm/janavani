import pytest

from src.config.runtime import (
    RuntimeConfigurationError,
    validate_runtime_configuration,
)


def test_development_allows_defaults():
    validate_runtime_configuration(
        environment="development",
        environ={},
    )


def test_production_requires_durable_providers():
    with pytest.raises(RuntimeConfigurationError):
        validate_runtime_configuration(
            environment="production",
            environ={},
        )


def test_production_accepts_durable_configuration():
    environ = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER": "transient",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://example",
        "JANAVANI_IDENTITY_LINKS_DSN": "postgresql://identity-role.example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
        "JANAVANI_IDENTITY_ASSERTION_SECRET": "test-secret",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER": "janavani-identity",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE": "janavani-api",
    }
    validate_runtime_configuration(
        environment="production",
        environ=environ,
    )


def test_production_rejects_shared_dsn_for_identity_mapping():
    environ = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER": "transient",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://shared-role.example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
    }
    with pytest.raises(
        RuntimeConfigurationError,
        match="JANAVANI_IDENTITY_ASSERTION_SECRET",
    ):
        validate_runtime_configuration(environment="production", environ=environ)


@pytest.mark.parametrize(
    "missing_setting",
    [
        "JANAVANI_IDENTITY_ASSERTION_SECRET",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE",
    ],
)
def test_production_requires_explicit_identity_assertion_trust_settings(missing_setting):
    environ = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER": "transient",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://example",
        "JANAVANI_IDENTITY_LINKS_DSN": "postgresql://identity-role.example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
        "JANAVANI_IDENTITY_ASSERTION_SECRET": "test-secret",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER": "janavani-identity",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE": "janavani-api",
    }
    environ.pop(missing_setting)
    with pytest.raises(RuntimeConfigurationError, match=missing_setting):
        validate_runtime_configuration(environment="production", environ=environ)



def test_production_runtime_contract_selects_the_validated_case_provider() -> None:
    from src.storage.provider_composition import ProviderComposition

    environ = {
        "JANAVANI_RUNTIME_MODE": "production",
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER": "transient",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://example",
        "JANAVANI_IDENTITY_LINKS_DSN": "postgresql://identity-role.example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
        "JANAVANI_IDENTITY_ASSERTION_SECRET": "test-secret",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER": "janavani-identity",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE": "janavani-api",
    }
    validate_runtime_configuration(environment="production", environ=environ)
    composition = ProviderComposition.from_environment(environ)

    assert composition.provider_for("civic_case") == "postgres"
    assert composition.provider_for("document_artifact") == "postgres"
    assert composition.provider_for("consent") == "postgres"
    assert composition.provider_for("submission") == "postgres"
    assert composition.provider_for("document_review") == "transient"
    assert composition.provider_for("authority") == "postgres"



def test_production_requires_explicit_transient_document_review_policy() -> None:
    environ = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://example",
        "JANAVANI_IDENTITY_LINKS_DSN": "postgresql://identity-role.example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
        "JANAVANI_IDENTITY_ASSERTION_SECRET": "test-secret",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER": "janavani-identity",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE": "janavani-api",
    }
    with pytest.raises(
        RuntimeConfigurationError,
        match="JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER=transient",
    ):
        validate_runtime_configuration(environment="production", environ=environ)

def test_telegram_factory_fails_closed_for_incomplete_production_configuration(monkeypatch):
    from src.bot_telegram import build_application

    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")
    required_settings = (
        "JANAVANI_CASE_REPOSITORY_PROVIDER",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER",
        "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER",
        "JANAVANI_IDENTITY_ASSERTION_SECRET",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE",
        "JANAVANI_POSTGRES_DSN",
        "JANAVANI_IDENTITY_LINKS_DSN",
        "JANAVANI_ARTIFACT_S3_BUCKET",
    )
    for name in required_settings:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(
        RuntimeConfigurationError,
        match="Production requires durable persistence providers",
    ):
        build_application(token="test-only-token")


def test_production_rejects_process_local_authority_directory():
    environ = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "memory",
    }
    with pytest.raises(RuntimeConfigurationError, match="JANAVANI_AUTHORITY_REPOSITORY_PROVIDER"):
        validate_runtime_configuration(environment="production", environ=environ)

def test_vercel_production_cannot_fall_back_to_development_defaults():
    with pytest.raises(RuntimeConfigurationError, match="Production requires durable persistence providers"):
        validate_runtime_configuration(environ={"VERCEL_ENV": "production"})


def test_managed_production_rejects_conflicting_development_mode():
    with pytest.raises(RuntimeConfigurationError, match="conflicts with JANAVANI_RUNTIME_MODE"):
        validate_runtime_configuration(
            environ={"VERCEL_ENV": "production", "JANAVANI_RUNTIME_MODE": "development"}
        )


def test_render_requires_explicit_runtime_mode():
    with pytest.raises(RuntimeConfigurationError, match="Render deployments must set JANAVANI_RUNTIME_MODE"):
        validate_runtime_configuration(environ={"RENDER_SERVICE_ID": "render-service-test"})

