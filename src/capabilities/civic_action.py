"""Small composition boundary for the first canonical civic-action slice."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.authority import AuthorityRepository, require_destination
from src.core.civic_case import CivicCase
from src.core.evidence import EvidenceRepository
from src.documents.document_contract import DocumentDraft, DocumentParty


@dataclass(frozen=True)
class CivicActionDraft:
    case: CivicCase
    document: DocumentDraft


def build_document_draft(
    case: CivicCase,
    *,
    document_id: str,
    date: str,
    authority_repository: AuthorityRepository,
    evidence_repository: EvidenceRepository | None = None,
) -> DocumentDraft:
    """Build a document from canonical Case + Authority data.

    Evidence validation is optional here because a document may be drafted
    before evidence is attached. If evidence is supplied, every case reference
    must resolve before the draft is produced.
    """
    if evidence_repository is not None:
        missing = [
            ref
            for ref in case.evidence_refs
            if evidence_repository.get(ref) is None
        ]
        if missing:
            raise ValueError(
                "Case references missing evidence: " + ", ".join(missing)
            )

    authority = authority_repository.get(case.related_office_id or "")
    if authority is None:
        raise ValueError("Case has no resolvable authority destination")

    destination = require_destination(authority)
    to = DocumentParty(
        name=destination.name,
        address=destination.address,
        email=destination.email,
        role=destination.role,
    )
    cc = tuple(
        DocumentParty(
            name=contact.name,
            address=contact.address,
            email=contact.email,
            role=contact.role,
        )
        for contact in authority.cc_contacts
    )

    return DocumentDraft(
        document_id=document_id,
        document_type=case.case_type.value,
        case_id=case.case_id,
        date=date,
        subject=case.subject,
        body=case.narrative,
        to=to,
        cc=cc,
    )
