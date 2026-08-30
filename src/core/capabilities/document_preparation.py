"""Shared document-preparation capability.

Preparation produces an editable structured draft. Rendering to PDF/DOCX is a
separate concern and remains user-selected. This layer does not send documents
by email or submit them to authorities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional
from uuid import uuid4

from src.core.contracts.case import Case, VerificationStatus


@dataclass(frozen=True)
class DocumentDraft:
    document_id: str
    document_type: str
    to_name: str
    to_address: str
    to_email: Optional[str]
    cc_name: Optional[str]
    cc_address: Optional[str]
    cc_email: Optional[str]
    subject: str
    body: str
    source_case_id: str
    editable: bool = True
    submission_enabled: bool = False
    metadata: dict = field(default_factory=dict)


class SharedDocumentPreparation:
    """Prepare a civic document from verified case context."""

    def prepare(
        self,
        case: Case,
        *,
        document_type: str = "complaint",
        to_name: str,
        to_address: str,
        to_email: Optional[str] = None,
        cc_name: Optional[str] = None,
        cc_address: Optional[str] = None,
        cc_email: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
    ) -> DocumentDraft:
        if not case.case_id:
            raise ValueError("case_id is required")
        if not case.authority or case.authority.verification != VerificationStatus.VERIFIED:
            raise ValueError("A verified authority is required before document preparation")
        if not to_name.strip() or not to_address.strip():
            raise ValueError("recipient name and address are required")

        generated_body = body or self._default_body(case)
        generated_subject = subject or f"Civic {document_type}: {case.category or 'Issue'}"

        return DocumentDraft(
            document_id=f"doc-{uuid4().hex[:16]}",
            document_type=document_type,
            to_name=to_name.strip(),
            to_address=to_address.strip(),
            to_email=to_email.strip() if to_email else None,
            cc_name=cc_name.strip() if cc_name else None,
            cc_address=cc_address.strip() if cc_address else None,
            cc_email=cc_email.strip() if cc_email else None,
            subject=generated_subject.strip(),
            body=generated_body.strip(),
            source_case_id=case.case_id,
        )

    @staticmethod
    def _default_body(case: Case) -> str:
        issue = case.issue_text.strip()
        category = case.category or "civic issue"
        return (
            "Subject: Civic issue requiring attention\n\n"
            f"I wish to bring to your attention the following {category} issue:\n\n"
            f"{issue}\n\n"
            "I request that the matter be examined and appropriate lawful action be taken."
        )
