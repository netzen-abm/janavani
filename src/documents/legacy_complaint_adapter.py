"""Compatibility adapter from legacy complaint data to DocumentDraft."""
from __future__ import annotations

from datetime import date

from src.core.authority import AuthorityRepository, require_destination
from src.documents.document_contract import DocumentDraft, DocumentParty


def complaint_to_document_draft(
    complaint: dict,
    *,
    document_id: str,
    case_id: str,
    authority_repository: AuthorityRepository,
) -> DocumentDraft:
    """Translate legacy complaint output without owning rendering or delivery."""
    office_id = str(complaint.get("office_id") or "")
    authority = authority_repository.get(office_id)
    if authority is None:
        raise ValueError("Complaint has no resolvable authority destination")

    destination = require_destination(authority)
    law = complaint.get("law") or {}
    legal_ground = None
    if law:
        legal_ground = " - ".join(
            value
            for value in (
                law.get("law"),
                law.get("section"),
                law.get("explanation"),
            )
            if value
        )

    user = complaint.get("user") or {}
    sender = DocumentParty(
        name=str(user.get("name") or "Not Provided"),
        address=str(user.get("address") or "Not Provided"),
    )

    return DocumentDraft(
        document_id=document_id,
        document_type="complaint",
        case_id=case_id,
        date=str(complaint.get("date") or date.today().strftime("%d-%m-%Y")),
        subject=str(complaint.get("issue") or "Citizen complaint")[:120],
        body=str(complaint.get("issue") or ""),
        to=DocumentParty(
            name=destination.name,
            address=destination.address,
            email=destination.email,
            role=destination.role,
        ),
        cc=tuple(
            DocumentParty(
                name=contact.name,
                address=contact.address,
                email=contact.email,
                role=contact.role,
            )
            for contact in authority.cc_contacts
        ),
        sender=sender,
        legal_ground=legal_ground,
    )
