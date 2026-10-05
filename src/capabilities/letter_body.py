"""Pure civic-letter body composition; no persistence or authorization."""
from __future__ import annotations

from .letter_drafting import LetterDraftRequest


def compose_letter_body(request: LetterDraftRequest) -> str:
    def _compose_body(request: LetterDraftRequest) -> str:
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
