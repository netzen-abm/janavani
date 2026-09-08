"""Canonical Constitutional Objection capability.

Builds an objection document from an owned canonical Case, a verified authority,
and a verified legislative profile. Rendering is delegated to the shared
artifact service; this capability never submits or transmits a document.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable
from uuid import uuid4

from src.capabilities.civic_case import CivicCaseCapability
from src.core.authority import AuthorityRepository, require_destination
from src.core.civic_case import CaseType
from src.core.evidence import EvidenceRepository
from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentDraft, DocumentFormat, DocumentParty
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.artifact_blob_factory import create_artifact_blob_store
from src.storage.repositories.artifact_provider import create_document_artifact_repository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.document_artifact import DocumentArtifactRepository


@dataclass(frozen=True)
class ConstitutionalObjectionBuildResult:
    case_id: str
    authority_id: str
    bill_code: str
    draft: DocumentDraft


class ConstitutionalObjectionCapability:
    """Surface-neutral Case → verified authority → objection document boundary."""

    def __init__(
        self,
        *,
        case_capability: CivicCaseCapability,
        case_repository: CivicCaseRepository,
        authority_repository: AuthorityRepository,
        bill_profile_loader: Callable[[str], dict[str, Any] | None],
        evidence_repository: EvidenceRepository | None = None,
        artifact_repository: DocumentArtifactRepository | None = None,
        blob_store: ArtifactBlobStore | None = None,
    ) -> None:
        self._case_capability = case_capability
        self._case_repository = case_repository
        self._authority_repository = authority_repository
        self._bill_profile_loader = bill_profile_loader
        self._evidence_repository = evidence_repository
        self._artifact_repository = artifact_repository
        self._blob_store = blob_store

    def build_document(
        self,
        case_id: str,
        *,
        identity: Any,
        bill_code: str,
        citizen_comments: str,
        document_id: str | None = None,
    ) -> ConstitutionalObjectionBuildResult:
        case = self._case_capability.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if case.case_type is not CaseType.OBJECTION:
            raise ValueError("Case is not an objection case")
        if not citizen_comments.strip():
            raise ValueError("Citizen reasoning is required")

        bill_data = self._bill_profile_loader(bill_code)
        if not bill_data:
            raise LookupError("Requested legislative bill index code not found")
        evaluation = bill_data.get("constitutional_evaluation")
        if not isinstance(evaluation, dict):
            raise ValueError("Legislative profile lacks constitutional evaluation")

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
        if not authority.verified:
            raise ValueError("Authority destination is not verified")
        destination = require_destination(authority)

        body = self._compose_body(bill_data, evaluation, citizen_comments)
        draft = DocumentDraft(
            document_id=document_id or f"doc-{uuid4().hex}",
            document_type=CaseType.OBJECTION.value,
            case_id=case.case_id,
            date=datetime.now(timezone.utc).date().isoformat(),
            subject=case.subject,
            body=body,
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
        return ConstitutionalObjectionBuildResult(
            case_id=case.case_id,
            authority_id=authority_id,
            bill_code=bill_code,
            draft=draft,
        )

    def generate_reviewable_artifact(
        self,
        case_id: str,
        *,
        identity: Any,
        bill_code: str,
        citizen_comments: str,
        document_format: DocumentFormat = DocumentFormat.PDF,
        output_dir: str | Path = "/tmp/janavani-artifacts/rendered",
        document_id: str | None = None,
    ) -> DocumentArtifact:
        result = self.build_document(
            case_id,
            identity=identity,
            bill_code=bill_code,
            citizen_comments=citizen_comments,
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
        case = self._case_capability.get_owned(case_id, identity=identity)
        if case is not None and artifact.reference.artifact_id not in case.document_refs:
            case.add_document(
                artifact.reference.artifact_id,
                event_id=f"{case.case_id}:document:{document_format.value}",
                occurred_at=datetime.now(timezone.utc).isoformat(),
                source_channel=None,
            )
            self._case_repository.save(case)
        return artifact

    def open_artifact(self, artifact: DocumentArtifact) -> BinaryIO:
        """Open generated bytes for the access surface; never transmits by itself."""
        store = self._blob_store or create_artifact_blob_store()
        return store.open(artifact.reference.storage_ref)

    @staticmethod
    def _compose_body(bill_data: dict[str, Any], evaluation: dict[str, Any], citizen_comments: str) -> str:
        state = bill_data["state"]
        title = bill_data["title"]
        return (
            "FORMAL PETITION OF OBJECTION / MEMORANDUM OF NON-COMPLIANCE\n"
            "====================================================================\n\n"
            f"The Legislative Assembly Secretariat / Standing Committee Board\n"
            f"Government of {state}\n\n"
            f"Subject: Formal Constitutional Objection Against '{title}'\n\n"
            "Respected Authority,\n\n"
            f"I am writing to register my formal objection to the proposed legislative draft titled '{title}'.\n\n"
            "CONSTITUTIONAL BREACH ANALYSIS:\n"
            f"1. ARTICLE 14 CLAUSE ASSESSMENT: {evaluation['article_14_analysis']}\n"
            f"2. ARTICLE 19 CLAUSE ASSESSMENT: {evaluation['article_19_analysis']}\n"
            f"3. ARTICLE 21 CLAUSE ASSESSMENT: {evaluation['article_21_analysis']}\n\n"
            "SUMMARY OF MATERIAL INCOMPLIANCE:\n"
            f"{evaluation['overall_constitutional_summary']}\n\n"
            "CITIZEN REASONING SUBMISSION:\n"
            f"\"{citizen_comments.strip()}\"\n\n"
            "The authority is requested to consider the stated objection and take appropriate action.\n\n"
            "Submitted Sincerely,\n"
            "A Concerned Citizen of India\n\n"
            "USER DELIVERY NOTICE:\n"
            "This file is generated for user review, printing, and download. JanaVani does not email or submit this document."
        )
