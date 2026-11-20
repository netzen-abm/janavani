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


def test_production_requires_postgres_authority_provider():
    environ = _valid_production_environment()
    environ.pop("JANAVANI_AUTHORITY_REPOSITORY_PROVIDER")
    with pytest.raises(RuntimeConfigurationError, match="JANAVANI_AUTHORITY_REPOSITORY_PROVIDER"):
        validate_runtime_configuration(environment="production", environ=environ)


def test_production_requires_postgres_consent_provider():
    environ = _valid_production_environment()
    environ.pop("JANAVANI_CONSENT_REPOSITORY_PROVIDER")
    with pytest.raises(RuntimeConfigurationError, match="JANAVANI_CONSENT_REPOSITORY_PROVIDER"):
        validate_runtime_configuration(environment="production", environ=environ)


def test_production_accepts_durable_configuration():
    validate_runtime_configuration(
        environment="production",
        environ=_valid_production_environment(),
    )


def test_production_rejects_shared_dsn_for_identity_mapping():
    environ = _valid_production_environment()
    environ.pop("JANAVANI_IDENTITY_LINKS_DSN")
    with pytest.raises(RuntimeConfigurationError, match="JANAVANI_IDENTITY_LINKS_DSN"):
        validate_runtime_configuration(environment="production", environ=environ)


def _valid_production_environment() -> dict[str, str]:
    return {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://example",
        "JANAVANI_IDENTITY_LINKS_DSN": "postgresql://identity-role.example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
    }
