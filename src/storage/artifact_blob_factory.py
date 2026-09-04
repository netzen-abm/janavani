"""Provider selection for artifact blob storage."""
from __future__ import annotations

import os

from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.local_artifact_blob import LocalArtifactBlobStore

SUPPORTED_ARTIFACT_BLOB_PROVIDERS = {"local", "s3"}


def create_artifact_blob_store(
    provider: str | None = None,
) -> ArtifactBlobStore:
    """Create a provider without coupling capabilities to it."""
    selected = (
        provider
        or os.getenv("JANAVANI_ARTIFACT_BLOB_PROVIDER")
        or "local"
    ).strip().lower()
    if selected == "local":
        root = os.getenv(
            "JANAVANI_ARTIFACT_BLOB_ROOT",
            "/tmp/janavani-artifacts",
        )
        return LocalArtifactBlobStore(root)
    if selected == "s3":
        from src.storage.s3_artifact_blob import S3ArtifactBlobStore

        return S3ArtifactBlobStore(
            prefix=os.getenv("JANAVANI_ARTIFACT_S3_PREFIX", "artifacts"),
            endpoint_url=os.getenv("JANAVANI_ARTIFACT_S3_ENDPOINT_URL"),
        )
    raise ValueError(
        f"Unsupported artifact blob provider: {selected}. "
        f"Supported providers: {sorted(SUPPORTED_ARTIFACT_BLOB_PROVIDERS)}"
    )
