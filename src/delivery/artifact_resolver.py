"""Reference resolver for user-approved document artifacts."""
from __future__ import annotations

import hashlib

from src.delivery.contract import DeliveryArtifact, DeliveryArtifactResolver
from src.documents.artifact_ref import ArtifactState
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.document_artifact import DocumentArtifactRepository


class ArtifactResolutionError(ValueError):
    """Raised when an artifact cannot be safely prepared for delivery."""


class RepositoryArtifactResolver(DeliveryArtifactResolver):
    """Resolve approved artifact metadata plus bytes without provider coupling."""

    _MEDIA_TYPES = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def __init__(
        self,
        *,
        artifact_repository: DocumentArtifactRepository,
        blob_store: ArtifactBlobStore,
    ) -> None:
        self._artifact_repository = artifact_repository
        self._blob_store = blob_store

    def resolve(self, *, artifact_id: str, case_id: str, document_id: str) -> DeliveryArtifact:
        artifact = self._artifact_repository.get(artifact_id)
        if artifact is None:
            raise ArtifactResolutionError("Delivery artifact was not found")
        if artifact.case_id != case_id:
            raise ArtifactResolutionError("Delivery artifact does not belong to the case")
        if artifact.document_id != document_id:
            raise ArtifactResolutionError("Delivery artifact does not belong to the document")
        if artifact.state is not ArtifactState.USER_APPROVED:
            raise ArtifactResolutionError("Only user-approved artifacts may be delivered")

        with self._blob_store.open(artifact.storage_ref) as stream:
            content = stream.read()

        actual_hash = hashlib.sha256(content).hexdigest()
        if artifact.content_sha256 and actual_hash != artifact.content_sha256.lower():
            raise ArtifactResolutionError("Delivery artifact content hash does not match metadata")

        media_type = self._MEDIA_TYPES.get(artifact.format.lower())
        if media_type is None:
            raise ArtifactResolutionError(f"Unsupported delivery artifact format: {artifact.format}")

        return DeliveryArtifact(
            artifact_id=artifact.artifact_id,
            document_id=artifact.document_id,
            case_id=artifact.case_id,
            format=artifact.format,
            content=content,
            content_sha256=actual_hash,
            media_type=media_type,
        )
