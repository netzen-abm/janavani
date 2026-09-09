"""Canonical review/edit contract for user-controlled document drafts.

Review is deliberately separate from generation and submission. A draft may be
edited by its owner before explicit approval; review never transmits anything.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.documents.document_contract import DocumentDraft


@dataclass(frozen=True)
class DocumentRevision:
    revision_id: str
    document_id: str
    case_id: str
    occurred_at: str
    actor_id: str
    subject: str
    body: str
    reason: str | None = None


class DocumentReviewContract:
    """Owner-scoped, deterministic document revision boundary."""

    def __init__(self, draft: DocumentDraft, *, owner_id: str) -> None:
        self._draft = draft
        self._owner_id = owner_id
        self._revisions: list[DocumentRevision] = []

    @property
    def draft(self) -> DocumentDraft:
        return self._draft

    @property
    def revisions(self) -> tuple[DocumentRevision, ...]:
        return tuple(self._revisions)

    def edit(
        self,
        *,
        actor_id: str,
        subject: str | None = None,
        body: str | None = None,
        reason: str | None = None,
    ) -> DocumentDraft:
        if actor_id != self._owner_id:
            raise PermissionError("Only the document owner can edit a draft")
        next_subject = self._draft.subject if subject is None else subject.strip()
        next_body = self._draft.body if body is None else body.strip()
        if not next_subject or not next_body:
            raise ValueError("A document requires a subject and body")
        self._draft = DocumentDraft(
            document_id=self._draft.document_id,
            document_type=self._draft.document_type,
            case_id=self._draft.case_id,
            date=self._draft.date,
            subject=next_subject,
            body=next_body,
            to=self._draft.to,
            cc=self._draft.cc,
            sender=self._draft.sender,
            legal_ground=self._draft.legal_ground,
        )
        self._revisions.append(DocumentRevision(
            revision_id=f"rev-{uuid4().hex}",
            document_id=self._draft.document_id,
            case_id=self._draft.case_id,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            actor_id=actor_id,
            subject=next_subject,
            body=next_body,
            reason=reason,
        ))
        return self._draft
