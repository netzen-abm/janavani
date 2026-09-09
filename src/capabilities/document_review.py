"""Shared user review/edit capability for generated document drafts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.capabilities.civic_case import CivicCaseCapability
from src.core.document_review import DocumentRevision
from src.documents.document_contract import DocumentDraft
from src.identity.context import IdentityContext
from src.storage.repositories.document_review import DocumentReviewRepository

CAPABILITY_ID = "document:review"


@dataclass(frozen=True)
class DocumentReviewRequest:
    document_id: str
    subject: str | None = None
    body: str | None = None
    reason: str | None = None


class DocumentReviewCapability:
    """Canonical owner-scoped edit boundary shared by all access surfaces."""

    def __init__(self, repository: DocumentReviewRepository, *, case_capability: CivicCaseCapability) -> None:
        self._repository = repository
        self._case_capability = case_capability

    def get_owned(self, document_id: str, *, identity: IdentityContext) -> DocumentDraft | None:
        draft = self._repository.get(document_id)
        if draft is None:
            return None
        case = self._case_capability.get_owned(draft.case_id, identity=identity)
        if case is None or document_id not in case.document_refs:
            return None
        return draft

    def edit(self, request: DocumentReviewRequest, *, identity: IdentityContext) -> DocumentDraft:
        draft = self.get_owned(request.document_id, identity=identity)
        if draft is None:
            raise LookupError("Document draft not found")
        decision = authorize(AuthorizationRequest(
            context=identity,
            capability=CAPABILITY_ID,
            action="edit",
            resource_id=draft.document_id,
        ))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to edit the document")
        subject = draft.subject if request.subject is None else request.subject.strip()
        body = draft.body if request.body is None else request.body.strip()
        if not subject or not body:
            raise ValueError("A document requires a subject and body")
        edited = DocumentDraft(
            document_id=draft.document_id,
            document_type=draft.document_type,
            case_id=draft.case_id,
            date=draft.date,
            subject=subject,
            body=body,
            to=draft.to,
            cc=draft.cc,
            sender=draft.sender,
            legal_ground=draft.legal_ground,
        )
        revision = DocumentRevision(
            revision_id=f"rev-{uuid4().hex}",
            document_id=edited.document_id,
            case_id=edited.case_id,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            actor_id=identity.principal.principal_id,
            subject=edited.subject,
            body=edited.body,
            reason=request.reason,
        )
        self._repository.save(edited)
        self._repository.save_revision(revision)
        return edited
