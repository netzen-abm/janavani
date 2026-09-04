"""Backward-compatible PDF API backed by the canonical document capability."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from src.core.authority import AuthorityRepository
from src.documents.document_contract import (
    DocumentDraft,
    DocumentFormat,
    DocumentParty,
)
from src.documents.renderers import render_document
from src.storage.repositories.authority_csv import CsvAuthorityRepository


def generate_pdf_from_complaint(
    complaint: dict,
    *,
    authority_repository: AuthorityRepository | None = None,
    output_dir: str | Path = ".",
) -> str:
    """Render a legacy complaint through the canonical document contract."""
    repository = authority_repository or CsvAuthorityRepository()
    authority = repository.get(str(complaint["office_id"]))
    if authority is None:
        raise ValueError(f"Unknown authority: {complaint['office_id']}")

    contact = authority.primary_contact
    if contact is None:
        raise ValueError(f"Authority has no primary contact: {authority.name}")

    user = complaint.get("user", {})
    law = complaint.get("law", {})
    legal_ground = ""
    if law:
        legal_ground = (
            f"{law.get('law', '')} {law.get('section', '')}\n"
            f"{law.get('explanation', '')}"
        ).strip()

    draft = DocumentDraft(
        document_id=str(complaint["complaint_id"]),
        document_type="complaint",
        case_id=str(complaint["complaint_id"]),
        date=str(complaint.get("date") or date.today()),
        subject=f"Complaint regarding {authority.name}",
        body=(
            "Respected Sir/Madam,\n\n"
            f"{complaint.get('issue', '')}\n\n"
            "I therefore request appropriate action and resolution.\n\n"
            "Thank you."
        ),
        to=DocumentParty(
            name=contact.name or authority.name,
            address=contact.address or authority.name,
            email=contact.email,
            role=contact.role,
        ),
        cc=tuple(
            DocumentParty(
                name=item.name,
                address=item.address or "",
                email=item.email,
                role=item.role,
            )
            for item in authority.cc_contacts
        ),
        sender=DocumentParty(
            name=str(user.get("name", "")),
            address=str(user.get("address", "")),
            email=user.get("email"),
            role="Citizen",
        ),
        legal_ground=legal_ground,
    )
    return render_document(draft, DocumentFormat.PDF, output_dir)


def generate_complaint_pdf(
    user_name: str,
    user_address: str,
    office_id: int | str,
    issue_text: str,
) -> str:
    """Preserve the historical signature without delivery behavior."""
    complaint = {
        "complaint_id": f"complaint-{office_id}",
        "office_id": office_id,
        "date": str(date.today()),
        "user": {"name": user_name, "address": user_address},
        "issue": issue_text,
    }
    return generate_pdf_from_complaint(complaint)
