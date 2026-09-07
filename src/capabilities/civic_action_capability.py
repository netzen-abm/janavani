"""Shared Case → Evidence → Authority → Document composition capability.

This boundary is surface-neutral. WebApp, Telegram and future access surfaces
must call this capability rather than rebuilding the civic-action chain.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.capabilities.civic_case import CivicCaseCapability
from src.core.authority import AuthorityRepository, require_destination
from src.core.civic_case import CivicCase
from src.core.evidence import EvidenceRepository
from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentDraft, DocumentFormat, DocumentParty
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.artifact_provider import create_document_artifact_repository
from src.storage.repositories.document_artifact import DocumentArtifactRepository


@dataclass(frozen=True)
class CivicActionBuildResult:
    """Canonical document draft produced from verified case dependencies."""

    case: CivicCase
    authority_id: str
    draft: DocumentDraft


class CivicActionCapability:
    """Compose canonical civic data into a reviewable document artifact."""

    def __init__(
        self,
        *,
        case_capability: CivicCaseCapability,
        authority_repository: AuthorityRepository,
        evidence_repository: EvidenceRepository | None = None,
        artifact_repository: DocumentArtifactRepository | None = None,
        blob_store: ArtifactBlobStore | None = None,
    ) -> None:
        self._case_capability = case_capability
        self._authority_repository = authority_repository
        self._evidence_repository = evidence_repository
        self._artifact_repository = artifact_repository
        self._blob_store = blob_store

    def build_document(
        self,
        case_id: str,
        *,
        identity,
        document_id: str | None = None,
        date: str | None = None,
    ) -> CivicActionBuildResult:
        """Build a document only from an owned canonical Case and resolvable authority."""
        case = self._case_capability.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")

        if self._evidence_repository is not None:
            missing = [
                evidence_id
                for evidence_id in case.evidence_refs
                if self._evidence_repository.get(evidence_id) is None
            ]
            if missing:
                raise ValueError("Case references missing evidence: " + ", ".join(missing))

        authority_id = str(case.related_office_id or "")
        authority = self._authority_repository.get(authority_id)
        if authority is None:
            raise ValueError("Case has no resolvable authority destination")
        destination = require_destination(authority)

        draft = DocumentDraft(
            document_id=document_id or f"doc-{uuid4().hex}",
            document_type=case.case_type.value,
            case_id=case.case_id,
            date=date or datetime.now(timezone.utc).date().isoformat(),
            subject=case.subject,
            body=case.narrative,
            to=DocumentParty(
                name=destination.name,
                address=destination.address,
                email=destination.email,
                role=destination.role,
            ),
            cc=tuple(
                DocumentParty(
                    name=contact.name,
                    address=contact.address,
                    email=contact.email,
                    role=contact.role,
                )
                for contact in authority.cc_contacts
            ),
        )
        return CivicActionBuildResult(case=case, authority_id=authority_id, draft=draft)

    def generate_reviewable_artifact(
        self,
        case_id: str,
        *,
        identity,
        document_format: DocumentFormat = DocumentFormat.PDF,
        output_dir: str | Path = "/tmp/janavani-artifacts/rendered",
        document_id: str | None = None,
    ) -> DocumentArtifact:
        """Generate an artifact for review/download; never submit or transmit it."""
        result = self.build_document(
            case_id,
            identity=identity,
            document_id=document_id,
        )
        artifact = generate_artifact(
            result.draft,
            document_format,
            output_dir,
            blob_store=self._blob_store,
        )
        repository = self._artifact_repository or create_document_artifact_repository()
        repository.save(artifact.reference)
        if artifact.reference.artifact_id not in result.case.document_refs:
            result.case.add_document(
                artifact.reference.artifact_id,
                event_id=f"{result.case.case_id}:document:{document_format.value}",
                occurred_at=datetime.now(timezone.utc).isoformat(),
                source_channel=None,
            )
            self._case_capability._repository.save(result.case)
        return artifact
