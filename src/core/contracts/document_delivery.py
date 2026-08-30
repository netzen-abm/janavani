"""Shared contract for citizen-reviewed document generation and delivery.

JanaVani's document workflow ends after delivering the user-selected PDF or
DOCX. Submission by email, post, printing, upload, or any other channel is
outside this capability.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    USER_REVIEW = "user_review"
    APPROVED = "approved"
    DELIVERED = "delivered"


@dataclass(frozen=True)
class DocumentAddress:
    name: str
    address: str
    email: Optional[str] = None


@dataclass(frozen=True)
class CivicDocument:
    document_id: str
    case_id: str
    document_type: str
    format: DocumentFormat
    to: DocumentAddress
    cc: tuple[DocumentAddress, ...] = ()
    content: str = ""
    status: DocumentStatus = DocumentStatus.DRAFT
