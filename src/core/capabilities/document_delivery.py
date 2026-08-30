"""Channel-neutral document preparation and delivery boundary."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.document_delivery import (
    CivicDocument,
    DocumentAddress,
    DocumentFormat,
    DocumentStatus,
)


class SharedDocumentDelivery:
    def prepare(
        self,
        *,
        case_id: str,
        document_type: str,
        content: str,
        authority: AuthorityCandidate,
        format: DocumentFormat,
    ) -> CivicDocument:
        if authority.status != AuthorityStatus.VERIFIED:
            raise ValueError("document recipient must be verified")
        if not content.strip():
            raise ValueError("document content is required")
        if not authority.to_address:
            raise ValueError("verified To address is required")
        to = DocumentAddress(authority.name, authority.to_address, authority.to_email)
        cc = ()
        if authority.cc_address:
            cc = (DocumentAddress("CC", authority.cc_address, authority.cc_email),)
        return CivicDocument(
            document_id=f"doc-{uuid4().hex[:12]}",
            case_id=case_id,
            document_type=document_type,
            format=format,
            to=to,
            cc=cc,
            content=content,
            status=DocumentStatus.USER_REVIEW,
        )

    def revise(self, document: CivicDocument, *, content: str | None = None, to: DocumentAddress | None = None, cc: tuple[DocumentAddress, ...] | None = None) -> CivicDocument:
        if document.status not in {DocumentStatus.USER_REVIEW, DocumentStatus.DRAFT}:
            raise ValueError("only a reviewable document can be revised")
        return replace(document, content=content if content is not None else document.content, to=to or document.to, cc=cc if cc is not None else document.cc)

    def approve(self, document: CivicDocument) -> CivicDocument:
        if document.status != DocumentStatus.USER_REVIEW:
            raise ValueError("document must be in user review before approval")
        return replace(document, status=DocumentStatus.APPROVED)

    def deliver(self, document: CivicDocument) -> CivicDocument:
        if document.status != DocumentStatus.APPROVED:
            raise ValueError("document must be approved before delivery")
        return replace(document, status=DocumentStatus.DELIVERED)
