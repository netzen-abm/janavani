"""Channel-neutral document contract for civic case workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    USER_APPROVED = "user_approved"
    EXPORTED = "exported"
    SUBMITTED = "submitted"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class PartyRef:
    party_type: str
    name: str
    postal_address: str | None = None
    email: str | None = None
    phone: str | None = None
    official_source_ref: str | None = None


@dataclass
class CivicDocument:
    document_id: str
    document_type: str
    title: str
    language: str
    to_party: PartyRef
    subject: str
    body: str
    from_party: PartyRef | None = None
    cc_parties: list[PartyRef] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    enclosures: list[str] = field(default_factory=list)
    version: int = 1
    status: DocumentStatus = DocumentStatus.DRAFT

    def approve(self) -> None:
        """Record explicit user approval before export/submission."""
        if not self.body.strip() or not self.subject.strip():
            raise ValueError("A document requires subject and body before approval")
        if self.version < 1:
            raise ValueError("Document version must be positive")
        self.status = DocumentStatus.USER_APPROVED

    def export(self) -> None:
        if self.status is not DocumentStatus.USER_APPROVED:
            raise ValueError("Only a user-approved document can be exported")
        self.status = DocumentStatus.EXPORTED

    def submit(self) -> None:
        if self.status not in {DocumentStatus.USER_APPROVED, DocumentStatus.EXPORTED}:
            raise ValueError("Only an approved or exported document can be submitted")
        self.status = DocumentStatus.SUBMITTED
