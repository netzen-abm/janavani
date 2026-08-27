"""Canonical channel-neutral civic document domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class DocumentType(str, Enum):
    COMPLAINT = "complaint"
    GRIEVANCE = "grievance"
    RTI = "rti"
    PETITION = "petition"
    REPRESENTATION = "representation"
    OBJECTION = "objection"
    APPEAL = "appeal"
    WHISTLEBLOWER = "whistleblower"
    OTHER = "other"


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


@dataclass(frozen=True)
class Document:
    """Versioned civic document metadata and text.

    Binary renderings are external artifacts referenced by the application
    layer; this object remains independent of PDF/DOCX providers.
    """

    document_id: str
    document_type: DocumentType
    title: str
    language: str
    to_party: PartyRef
    subject: str
    body: str
    from_party: PartyRef | None = None
    cc_parties: tuple[PartyRef, ...] = ()
    references: tuple[str, ...] = ()
    enclosures: tuple[str, ...] = ()
    version: int = 1
    status: DocumentStatus = DocumentStatus.DRAFT
    case_id: str | None = None
    artifact_ref: str | None = None
    content_hash: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        document_type: DocumentType,
        title: str,
        language: str,
        to_party: PartyRef,
        subject: str,
        body: str,
        *,
        case_id: str | None = None,
        from_party: PartyRef | None = None,
        cc_parties: list[PartyRef] | None = None,
        references: list[str] | None = None,
        enclosures: list[str] | None = None,
    ) -> "Document":
        values = {
            "title": title.strip(),
            "language": language.strip(),
            "subject": subject.strip(),
            "body": body.strip(),
        }
        if not values["title"]:
            raise ValueError("document title is required")
        if not values["language"]:
            raise ValueError("document language is required")
        if not values["subject"]:
            raise ValueError("document subject is required")
        if not values["body"]:
            raise ValueError("document body is required")
        if not to_party.name.strip():
            raise ValueError("document recipient is required")
        now = datetime.now(timezone.utc)
        return cls(
            document_id=f"DOC-{uuid4().hex[:12].upper()}",
            document_type=document_type,
            title=values["title"],
            language=values["language"],
            to_party=to_party,
            subject=values["subject"],
            body=values["body"],
            case_id=case_id.strip() if case_id else None,
            from_party=from_party,
            cc_parties=tuple(cc_parties or []),
            references=tuple(x.strip() for x in (references or []) if x.strip()),
            enclosures=tuple(x.strip() for x in (enclosures or []) if x.strip()),
            created_at=now,
            updated_at=now,
        )

    def approve(self) -> "Document":
        if self.status != DocumentStatus.DRAFT:
            raise ValueError("only draft documents can be user-approved")
        return self._with_status(DocumentStatus.USER_APPROVED)

    def export(self, *, artifact_ref: str, content_hash: str) -> "Document":
        if self.status not in {DocumentStatus.USER_APPROVED, DocumentStatus.EXPORTED}:
            raise ValueError("document must be user-approved before export")
        if not artifact_ref.strip() or not content_hash.strip():
            raise ValueError("artifact_ref and content_hash are required")
        return self._with_status(DocumentStatus.EXPORTED, artifact_ref=artifact_ref.strip(), content_hash=content_hash.strip())

    def mark_submitted(self) -> "Document":
        if self.status not in {DocumentStatus.EXPORTED, DocumentStatus.USER_APPROVED}:
            raise ValueError("document must be exported or approved before submission")
        return self._with_status(DocumentStatus.SUBMITTED)

    def _with_status(self, status: DocumentStatus, **changes: object) -> "Document":
        values = {
            "document_id": self.document_id,
            "document_type": self.document_type,
            "title": self.title,
            "language": self.language,
            "to_party": self.to_party,
            "subject": self.subject,
            "body": self.body,
            "from_party": self.from_party,
            "cc_parties": self.cc_parties,
            "references": self.references,
            "enclosures": self.enclosures,
            "version": self.version,
            "status": status,
            "case_id": self.case_id,
            "artifact_ref": self.artifact_ref,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "updated_at": datetime.now(timezone.utc),
        }
        values.update(changes)
        return Document(**values)


__all__ = ["Document", "DocumentStatus", "DocumentType", "PartyRef"]
