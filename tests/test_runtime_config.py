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
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
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
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
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
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
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
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
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
