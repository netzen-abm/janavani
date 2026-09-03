"""Canonical, channel-neutral document draft contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


@dataclass(frozen=True)
class DocumentParty:
    name: str
    address: str = ""
    email: str | None = None
    role: str | None = None


@dataclass(frozen=True)
class DocumentDraft:
    document_id: str
    document_type: str
    case_id: str
    date: str
    subject: str
    body: str
    to: DocumentParty
    cc: tuple[DocumentParty, ...] = field(default_factory=tuple)
    sender: DocumentParty | None = None
    legal_ground: str | None = None

    def as_text(self) -> str:
        lines = [
            f"Document ID: {self.document_id}",
            f"Case ID: {self.case_id}",
            f"Date: {self.date}",
            "",
            "To:",
            self.to.role or self.to.name,
            self.to.name,
            self.to.address,
        ]
        if self.to.email:
            lines.append(f"Email: {self.to.email}")
        if self.sender:
            lines.extend(["", "From:", self.sender.name, self.sender.address])
            if self.sender.email:
                lines.append(f"Email: {self.sender.email}")
        if self.cc:
            lines.extend(["", "CC:"])
            for party in self.cc:
                label = party.role or party.name
                lines.append(f"{label} | {party.name}")
                if party.address:
                    lines.append(party.address)
                if party.email:
                    lines.append(f"Email: {party.email}")
        lines.extend(["", f"Subject: {self.subject}", "", self.body])
        if self.legal_ground:
            lines.extend(["", "Legal Ground:", self.legal_ground])
        return "\n".join(line for line in lines if line is not None)
