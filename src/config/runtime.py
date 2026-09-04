"""Runtime configuration validation for provider-independent deployments."""
from __future__ import annotations

import os


class RuntimeConfigurationError(RuntimeError):
    """Raised when runtime configuration violates a deployment contract."""


def validate_runtime_configuration(
    *,
    environment: str | None = None,
    environ: dict[str, str] | None = None,
) -> None:
    """Fail closed when production would use process-local persistence."""
    values = os.environ if environ is None else environ
    mode = (environment or values.get("JANAVANI_RUNTIME_MODE", "development"))
    mode = mode.strip().lower()
    if mode not in {"development", "test", "production"}:
        raise RuntimeConfigurationError(
            f"Unsupported JANAVANI_RUNTIME_MODE: {mode}"
        )
    if mode != "production":
        return

    required = {
        "JANAVANI_CASE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_EVIDENCE_REPOSITORY_PROVIDER": "postgres",
        "JANAVANI_ARTIFACT_BLOB_PROVIDER": "s3",
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

    if not values.get("JANAVANI_POSTGRES_DSN"):
        raise RuntimeConfigurationError(
            "Production PostgreSQL providers require JANAVANI_POSTGRES_DSN"
        )
    if not values.get("JANAVANI_ARTIFACT_S3_BUCKET"):
        raise RuntimeConfigurationError(
            "Production artifact storage requires JANAVANI_ARTIFACT_S3_BUCKET"
        )
