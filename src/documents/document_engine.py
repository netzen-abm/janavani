"""Canonical entry point for channel-neutral civic document composition."""

from __future__ import annotations

from documents.complaint_builder import build_complaint
from documents.document_contract import DocumentRequest, StructuredDocument


class DocumentEngine:
    """Compose structured documents without owning rendering or delivery."""

    def generate(self, request: DocumentRequest) -> StructuredDocument:
        if request.document_type == "complaint":
            return build_complaint(
                user_name=request.user_name,
                user_address=request.user_address,
                office_id=request.office_id,
                issue_text=request.issue_text,
                language=request.language,
            )
        raise ValueError(f"Unsupported document type: {request.document_type}")
