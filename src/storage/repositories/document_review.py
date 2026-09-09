"""Provider-neutral persistence contract for reviewable document drafts."""
from __future__ import annotations

from typing import Protocol

from src.core.document_review import DocumentRevision
from src.documents.document_contract import DocumentDraft


class DocumentReviewRepository(Protocol):
    def get(self, document_id: str) -> DocumentDraft | None: ...

    def save(self, draft: DocumentDraft) -> None: ...

    def revisions(self, document_id: str) -> list[DocumentRevision]: ...

    def save_revision(self, revision: DocumentRevision) -> None: ...


class InMemoryDocumentReviewRepository:
    """Deterministic reference provider for tests and local development."""

    def __init__(self) -> None:
        self._drafts: dict[str, DocumentDraft] = {}
        self._revisions: dict[str, list[DocumentRevision]] = {}

    def get(self, document_id: str) -> DocumentDraft | None:
        return self._drafts.get(document_id)

    def save(self, draft: DocumentDraft) -> None:
        self._drafts[draft.document_id] = draft

    def revisions(self, document_id: str) -> list[DocumentRevision]:
        return list(self._revisions.get(document_id, []))

    def save_revision(self, revision: DocumentRevision) -> None:
        self._revisions.setdefault(revision.document_id, []).append(revision)
