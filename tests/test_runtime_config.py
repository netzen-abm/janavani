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
        "JANAVANI_POSTGRES_DSN": "postgresql://example",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
    }
    validate_runtime_configuration(
        environment="production",
        environ=environ,
    )
