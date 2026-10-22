"""Provider-neutral persistence contract for reviewable document drafts."""
from __future__ import annotations

from threading import RLock
from time import monotonic
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



class TransientDocumentReviewRepository:
    """Bounded in-process drafts; content expires and is never written to disk."""

    def __init__(self, *, ttl_seconds: int = 900, max_entries: int = 1000) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._drafts: dict[str, DocumentDraft] = {}
        self._revisions: dict[str, list[DocumentRevision]] = {}
        self._expires: dict[str, float] = {}
        self._lock = RLock()

    def _forget(self, document_id: str) -> None:
        self._drafts.pop(document_id, None)
        self._revisions.pop(document_id, None)
        self._expires.pop(document_id, None)

    def _purge(self, now: float) -> None:
        for document_id, expiry in list(self._expires.items()):
            if expiry <= now:
                self._forget(document_id)

    def _make_room(self, document_id: str) -> None:
        if document_id not in self._drafts and len(self._drafts) >= self._max_entries:
            oldest = min(self._expires, key=self._expires.get)
            self._forget(oldest)

    def get(self, document_id: str) -> DocumentDraft | None:
        with self._lock:
            self._purge(monotonic())
            return self._drafts.get(document_id)

    def save(self, draft: DocumentDraft) -> None:
        with self._lock:
            now = monotonic()
            self._purge(now)
            self._make_room(draft.document_id)
            self._drafts[draft.document_id] = draft
            self._expires[draft.document_id] = now + self._ttl

    def revisions(self, document_id: str) -> list[DocumentRevision]:
        with self._lock:
            self._purge(monotonic())
            return list(self._revisions.get(document_id, []))

    def save_revision(self, revision: DocumentRevision) -> None:
        with self._lock:
            now = monotonic()
            self._purge(now)
            if revision.document_id not in self._drafts:
                raise LookupError("Transient document draft has expired or does not exist")
            self._revisions.setdefault(revision.document_id, []).append(revision)
            self._expires[revision.document_id] = now + self._ttl

    def clear(self) -> None:
        """Clear all transient review drafts and revisions."""
        with self._lock:
            self._drafts.clear()
            self._revisions.clear()
            self._expires.clear()
