from pathlib import Path

import pytest

from src.storage.artifact_blob_factory import (
    ArtifactBlobProviderConfigurationError,
    create_artifact_blob_store,
)
from src.storage.local_artifact_blob import LocalArtifactBlobStore


def test_local_provider_can_be_selected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    monkeypatch.setenv("JANAVANI_ARTIFACT_BLOB_PROVIDER", "local")
    monkeypatch.setenv("JANAVANI_ARTIFACT_BLOB_ROOT", str(tmp_path))

    store = create_artifact_blob_store()

    assert isinstance(store, LocalArtifactBlobStore)


def test_unknown_provider_fails_closed():
    with pytest.raises(ArtifactBlobProviderConfigurationError):
        create_artifact_blob_store("unknown")


def test_s3_provider_requires_bucket(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("JANAVANI_ARTIFACT_S3_BUCKET", raising=False)

    with pytest.raises(ArtifactBlobProviderConfigurationError):
        create_artifact_blob_store("s3")
