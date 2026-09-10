from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from src.delivery.artifact_resolver import ArtifactResolutionError, RepositoryArtifactResolver
from src.documents.artifact_ref import ArtifactState, DocumentArtifactRef
from src.storage.local_artifact_blob import LocalArtifactBlobStore
from src.storage.repositories.document_artifact import InMemoryDocumentArtifactRepository


def _resolver(tmp_path: Path, *, state: ArtifactState = ArtifactState.USER_APPROVED):
    content = b"approved civic document"
    digest = hashlib.sha256(content).hexdigest()
    blobs = LocalArtifactBlobStore(tmp_path)
    stored = blobs.put("case-1/document-1.pdf", content, media_type="application/pdf")
    artifacts = InMemoryDocumentArtifactRepository()
    artifacts.save(
        DocumentArtifactRef(
            artifact_id="artifact-1",
            document_id="document-1",
            case_id="case-1",
            format="pdf",
            storage_ref=stored.storage_ref,
            content_sha256=digest,
            state=state,
        )
    )
    return RepositoryArtifactResolver(artifact_repository=artifacts, blob_store=blobs)


def test_resolves_only_user_approved_artifact(tmp_path: Path) -> None:
    artifact = _resolver(tmp_path).resolve(
        artifact_id="artifact-1", case_id="case-1", document_id="document-1"
    )
    assert artifact.content == b"approved civic document"
    assert artifact.content_sha256 == hashlib.sha256(artifact.content).hexdigest()
    assert artifact.media_type == "application/pdf"


def test_rejects_unapproved_artifact(tmp_path: Path) -> None:
    resolver = _resolver(tmp_path, state=ArtifactState.GENERATED)
    with pytest.raises(ArtifactResolutionError, match="user-approved"):
        resolver.resolve(artifact_id="artifact-1", case_id="case-1", document_id="document-1")


def test_rejects_cross_case_artifact(tmp_path: Path) -> None:
    resolver = _resolver(tmp_path)
    with pytest.raises(ArtifactResolutionError, match="case"):
        resolver.resolve(artifact_id="artifact-1", case_id="case-2", document_id="document-1")


def test_rejects_hash_mismatch(tmp_path: Path) -> None:
    resolver = _resolver(tmp_path)
    # The repository metadata is authoritative for the expected hash; corrupting the
    # stored bytes must therefore fail before an external transport can see them.
    artifact = resolver._artifact_repository.get("artifact-1")
    assert artifact is not None
    resolver._blob_store.delete(artifact.storage_ref)
    stored = resolver._blob_store.put(
        "case-1/document-1.pdf", b"tampered document", media_type="application/pdf"
    )
    resolver._artifact_repository.save(
        DocumentArtifactRef(
            artifact_id=artifact.artifact_id,
            document_id=artifact.document_id,
            case_id=artifact.case_id,
            format=artifact.format,
            storage_ref=stored.storage_ref,
            content_sha256=artifact.content_sha256,
            state=artifact.state,
        )
    )
    with pytest.raises(ArtifactResolutionError, match="hash"):
        resolver.resolve(artifact_id="artifact-1", case_id="case-1", document_id="document-1")
