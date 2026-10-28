"""Pure civic-letter body composition; no persistence or authorization."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .letter_drafting import LetterDraftRequest


def compose_letter_body(request: LetterDraftRequest) -> str:
    sections = [
        "NOTICE TO THE RECIPIENT",
        "",
        "This notice records the sender's stated position and requests a "
        "documented response. Statements of legal effect remain the sender's "
        "position unless supported by applicable authority.",
        "",
        "I. OPENING",
        request.issue.strip(),
    ]
    if request.proposal_or_notice.strip():
        sections.extend(["", "PROPOSAL / NOTICE", request.proposal_or_notice.strip()])
    if request.part_i_interrogatories:
        sections.extend(["", "PART I — INTERROGATORIES"])
        sections.extend(
        f"{i}. {item}"
        for i, item in enumerate(request.part_i_interrogatories, 1)
        )
    if request.legal_framework:
        sections.extend(["", "PART II — CONSTITUTIONAL / LEGAL FRAMEWORK"])
        sections.extend(f"- {item}" for item in request.legal_framework)
    if request.requested_conditions:
        sections.extend(["", "PART III — REQUESTED CONDITIONS"])
        sections.extend(f"- {item}" for item in request.requested_conditions)
    if request.requested_documents:
        sections.extend(["", "REQUESTED DOCUMENTS / RECORDS"])
        sections.extend(f"- {item}" for item in request.requested_documents)
    if request.jurisdiction:
        sections.extend(["", f"JURISDICTION: {request.jurisdiction.strip()}"])
    if request.response_period:
        sections.extend(["", f"RESPONSE PERIOD: {request.response_period.strip()}"])
    if request.deadline_date:
        sections.extend(["", f"REQUESTED DEADLINE: {request.deadline_date.strip()}"])
    if request.remedies_reserved:
        sections.extend(["", "REMEDIES / RIGHTS RESERVED"])
        sections.extend(f"- {item}" for item in request.remedies_reserved)
    if request.references:
        sections.extend(["", "REFERENCES"])
        sections.extend(f"- {item}" for item in request.references)
    if request.evidence_refs:
        sections.extend(["", "EVIDENCE REFERENCES"])
        sections.extend(f"- {item}" for item in request.evidence_refs)
    if request.provenance_refs:
        sections.extend(["", "PROVENANCE REFERENCES"])
        sections.extend(f"- {item}" for item in request.provenance_refs)
    sections.extend([
        "",
        "REVIEW / APPROVAL",
        "This document requires citizen review and explicit approval "
        "before any consequential submission action.",
    ])
    return "\n".join(sections)

def compose_template_body(request: LetterDraftRequest, template) -> str:
    """Render citizen values into an approved structure without mutating the template."""
    from src.documents.template_catalogue import CivicDocumentTemplate

    if not isinstance(template, CivicDocumentTemplate):
        raise TypeError("An approved civic document template is required")
    sections = [
        template.title,
        "",
        template.introduction,
        "",
        "SUBJECT",
        request.subject.strip(),
        "",
        "DRAFT ONLY — verify facts, recipient, jurisdiction and applicable procedure.",
    ]
    values = {
        "document_header": (),
        "issue": request.issue.strip(),
        "proposal_or_notice": request.proposal_or_notice.strip(),
        "part_i_interrogatories": request.part_i_interrogatories,
        "legal_framework": request.legal_framework,
        "requested_conditions": request.requested_conditions,
        "requested_documents": request.requested_documents,
        "remedies_reserved": request.remedies_reserved,
        "references": request.references,
        "evidence_refs": request.evidence_refs,
        "provenance_refs": request.provenance_refs,
        "response_period": request.response_period,
        "deadline_date": request.deadline_date,
        "jurisdiction": request.jurisdiction,
    }
    for section in template.sections:
        value = values.get(section.field_name)
        if section.default_items:
            if isinstance(value, (tuple, list)):
                # The curated, non-personal starter structure remains available;
                # citizen-supplied items extend it without duplicating exact entries.
                value = section.default_items + tuple(
                    item for item in value if item not in section.default_items
                )
            elif not value:
                value = section.default_items
        if not value:
            continue
        sections.extend(["", section.heading])
        if isinstance(value, (tuple, list)):
            if section.field_name == "part_i_interrogatories":
                sections.extend(f"{index}. {item}" for index, item in enumerate(value, 1))
            elif section.field_name == "document_header":
                sections.extend(item.splitlines() for item in ())
                sections.extend(line for item in value for line in item.splitlines())
            else:
                sections.extend(f"- {item}" for item in value)
        else:
            sections.append(str(value).strip())
    sections.extend([
        "",
        "REVIEW / APPROVAL",
        "Review and edit this document before use. Janavani has not submitted or sent it.",
        "The template is a structural starting point, not legal advice or a guarantee of legal effect.",
        "Complete or remove every bracketed prompt and verify all facts and citations before sending.",
    ])
    return "\n".join(sections)
