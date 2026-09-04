"""Provider selection for artifact blob storage."""
from __future__ import annotations

import os

from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.local_artifact_blob import LocalArtifactBlobStore

SUPPORTED_ARTIFACT_BLOB_PROVIDERS = {"local", "s3"}


class ArtifactBlobProviderConfigurationError(RuntimeError):
    """Raised when artifact blob storage is misconfigured."""


def create_artifact_blob_store(
    provider: str | None = None,
) -> ArtifactBlobStore:
    """Create a provider without coupling capabilities to it."""
    selected = (
        provider
        or os.getenv("JANAVANI_ARTIFACT_BLOB_PROVIDER")
        or "local"
    ).strip().lower()

    if selected not in SUPPORTED_ARTIFACT_BLOB_PROVIDERS:
        raise ArtifactBlobProviderConfigurationError(
            f"Unsupported artifact blob provider: {selected}. "
            f"Supported providers: "
            f"{sorted(SUPPORTED_ARTIFACT_BLOB_PROVIDERS)}"
        )

    if selected == "local":
        root = os.getenv(
            "JANAVANI_ARTIFACT_BLOB_ROOT",
            "/tmp/janavani-artifacts",
        )
        return LocalArtifactBlobStore(root)

    from src.storage.s3_artifact_blob import S3ArtifactBlobStore

    try:
        return S3ArtifactBlobStore(
            prefix=os.getenv(
                "JANAVANI_ARTIFACT_S3_PREFIX",
                "artifacts",
            ),
            endpoint_url=os.getenv(
                "JANAVANI_ARTIFACT_S3_ENDPOINT_URL"
            ),
        )
    except (ValueError, TypeError) as exc:
        raise ArtifactBlobProviderConfigurationError(
            "S3 artifact provider requires a configured bucket"
        ) from exc
