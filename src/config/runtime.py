"""Runtime configuration validation for provider-independent deployments."""
from __future__ import annotations

import os
from collections.abc import Mapping
from urllib.parse import urlsplit


class RuntimeConfigurationError(RuntimeError):
    """Raised when runtime configuration violates a deployment contract."""


def resolve_runtime_mode(
    *,
    environment: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Resolve one platform-aware runtime mode for every Python surface."""
    values = os.environ if environ is None else environ
    # An explicit test override keeps unit tests deterministic. Otherwise,
    # deployment-platform context outranks a permissive local-development default.
    if environment is not None:
        mode = environment
    else:
        explicit_mode = values.get("JANAVANI_RUNTIME_MODE", "").strip().lower()
        vercel_environment = values.get("VERCEL_ENV", "").strip().lower()
        railway_environment = values.get("RAILWAY_ENVIRONMENT_NAME", "").strip().lower()
        is_vercel_production = vercel_environment == "production"
        is_railway_production = railway_environment == "production"
        if is_vercel_production or is_railway_production:
            if explicit_mode and explicit_mode != "production":
                raise RuntimeConfigurationError(
                    "Managed production deployment conflicts with JANAVANI_RUNTIME_MODE; use production"
                )
            mode = "production"
        elif explicit_mode:
            mode = explicit_mode
        elif vercel_environment == "preview" or railway_environment:
            mode = "test"
        elif vercel_environment == "development":
            mode = "development"
        elif values.get("RENDER_SERVICE_ID") or values.get("RENDER", "").strip().lower() in {"true", "1"}:
            raise RuntimeConfigurationError(
                "Render deployments must set JANAVANI_RUNTIME_MODE explicitly"
            )
        else:
            mode = "development"
    mode = mode.strip().lower()
    if mode not in {"development", "test", "production"}:
        raise RuntimeConfigurationError(
            f"Unsupported JANAVANI_RUNTIME_MODE: {mode}"
        )
    return mode

def validate_identity_dsn_contract(values: Mapping[str, str]) -> str:
    """Require a distinct DSN authenticated as the dedicated identity role."""
    identity_dsn = values.get("JANAVANI_IDENTITY_LINKS_DSN", "").strip()
    if not identity_dsn:
        raise RuntimeConfigurationError(
            "Production identity mapping requires dedicated JANAVANI_IDENTITY_LINKS_DSN"
        )
    postgres_dsn = values.get("JANAVANI_POSTGRES_DSN", "").strip()
    if not postgres_dsn:
        raise RuntimeConfigurationError(
            "Production PostgreSQL providers require JANAVANI_POSTGRES_DSN"
        )
    if identity_dsn == postgres_dsn:
        raise RuntimeConfigurationError(
            "Production identity mapping requires a separate identity DSN; "
            "JANAVANI_IDENTITY_LINKS_DSN must be distinct from JANAVANI_POSTGRES_DSN"
        )
    try:
        identity_login_role = urlsplit(identity_dsn).username
    except ValueError:
        identity_login_role = None
    if identity_login_role != "janavani_identity_service":
        raise RuntimeConfigurationError(
            "Production identity mapping DSN must authenticate as "
            "the dedicated janavani_identity_service role"
        )
    return identity_dsn


def validate_runtime_configuration(
    *,
    environment: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> None:
    """Fail closed when production would use process-local persistence."""
    values = os.environ if environ is None else environ
    mode = resolve_runtime_mode(environment=environment, environ=values)
    if mode != "production":
        return

    required = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_AUTHORITY_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_CONSENT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_SUBMISSION_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
        "JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER": "postgres",
    }
    mismatches = [
        f"{name}={values.get(name)!r} (expected {expected!r})"
        for name, expected in required.items()
        if values.get(name, "").strip().lower() != expected
    ]
    if mismatches:
        detail = "; ".join(mismatches)
        raise RuntimeConfigurationError(
            "Production requires durable persistence providers: " + detail
        )

    if values.get("JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER", "").strip().lower() != "transient":
        raise RuntimeConfigurationError(
            "Production document review requires "
            "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER=transient "
            "until a durable citizen-content adapter is explicitly approved"
        )

    identity_assertion_settings = (
        "JANAVANI_IDENTITY_ASSERTION_SECRET",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE",
    )
    missing_identity_settings = [
        name for name in identity_assertion_settings
        if not values.get(name, "").strip()
    ]
    if missing_identity_settings:
        raise RuntimeConfigurationError(
            "Production authenticated identity requires explicit assertion configuration: "
            + ", ".join(missing_identity_settings)
        )

    if not values.get("JANAVANI_POSTGRES_DSN"):
        raise RuntimeConfigurationError(
            "Production PostgreSQL providers require JANAVANI_POSTGRES_DSN"
        )
    validate_identity_dsn_contract(values)
    if not values.get("JANAVANI_ARTIFACT_S3_BUCKET"):
        raise RuntimeConfigurationError(
            "Production artifact storage requires JANAVANI_ARTIFACT_S3_BUCKET"
        )
