"""Managed deployment environments must not fall back to development persistence."""
import pytest

from src.config.runtime import RuntimeConfigurationError, validate_runtime_configuration


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



@pytest.mark.parametrize(
    ("platform_variable", "platform_value"),
    [("VERCEL_ENV", "production"), ("RAILWAY_ENVIRONMENT_NAME", "production")],
)
def test_telegram_factory_fails_closed_on_managed_production(
    monkeypatch, platform_variable, platform_value
):
    from src.bot_telegram import build_application

    monkeypatch.setenv(platform_variable, platform_value)
    monkeypatch.delenv("JANAVANI_RUNTIME_MODE", raising=False)
    for name in (
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
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(
        RuntimeConfigurationError,
        match="Production requires durable persistence providers",
    ):
        build_application(token="test-only-token")



def test_production_rejects_identity_dsn_for_a_different_login_role():
    settings = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER": "transient",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_POSTGRES_DSN": "postgresql://janavani_case_runtime:secret@db.example/janavani",
        "JANAVANI_IDENTITY_LINKS_DSN": "postgresql://janavani_case_runtime:secret@db.example/janavani_identity",
        "JANAVANI_ARTIFACT_S3_BUCKET": "janavani-artifacts",
        "JANAVANI_IDENTITY_ASSERTION_SECRET": "test-secret",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER": "janavani-identity",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE": "janavani-api",
    }
    with pytest.raises(RuntimeConfigurationError, match="janavani_identity_service role"):
        validate_runtime_configuration(environment="production", environ=settings)
