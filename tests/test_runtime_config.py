from pathlib import Path

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



def test_render_canonical_api_declares_production_persistence_and_identity_gates():
    manifest = Path(__file__).resolve().parents[1] / "render.yaml"
    source = manifest.read_text(encoding="utf-8")
    api_service = source.split("name: janavani-web-api", 1)[1].split(
        "\n  - type: web", 1
    )[0]

    required_values = {
        "JANAVANI_RUNTIME_MODE": "production",
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_CITIZEN_DOCUMENT_FORMAT_REPOSITORY_PROVIDER": "postgres",
    }
    for key, value in required_values.items():
        assert f"key: {key}" in api_service
        assert f"value: {value}" in api_service

    required_secrets = (
        "JANAVANI_POSTGRES_DSN",
        "JANAVANI_IDENTITY_LINKS_DSN",
        "JANAVANI_ARTIFACT_S3_BUCKET",
        "JANAVANI_CITIZEN_DOCUMENT_FORMAT_DSN",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "JANAVANI_IDENTITY_ASSERTION_SECRET",
        "JANAVANI_IDENTITY_REPLAY_REDIS_URL",
    )
    for key in required_secrets:
        assert f"key: {key}\n        sync: false" in api_service

    assert "JANAVANI_IDENTITY_ASSERTION_ISSUER" in api_service
    assert "JANAVANI_IDENTITY_ASSERTION_AUDIENCE" in api_service
