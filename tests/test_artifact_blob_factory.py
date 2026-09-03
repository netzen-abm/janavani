from pathlib import Path

import pytest

from src.storage.artifact_blob_factory import create_artifact_blob_store
from src.storage.local_artifact_blob import LocalArtifactBlobStore


def test_local_provider_can_be_selected(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("JANAVANI_ARTIFACT_BLOB_PROVIDER", "local")
    monkeypatch.setenv("JANAVANI_ARTIFACT_BLOB_ROOT", str(tmp_path))

    store = create_artifact_blob_store()

    assert isinstance(store, LocalArtifactBlobStore)


def test_unknown_provider_fails_closed():
    with pytest.raises(ValueError):
        create_artifact_blob_store("unknown")
