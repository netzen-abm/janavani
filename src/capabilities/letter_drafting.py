"""Canonical, surface-neutral civic letter drafting capability."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum

from src.capabilities.civic_action_capability import CivicActionCapability
from src.documents.document_contract import DocumentDraft


class LetterDraftStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"


@dataclass(frozen=True)
class LetterDraftRequest:
    """Citizen-controlled content used to compose a notice/representation."""

    subject: str
    issue: str
    proposal_or_notice: str = ""
    part_i_interrogatories: tuple[str, ...] = field(default_factory=tuple)
    legal_framework: tuple[str, ...] = field(default_factory=tuple)
    requested_conditions: tuple[str, ...] = field(default_factory=tuple)
    requested_documents: tuple[str, ...] = field(default_factory=tuple)
    remedies_reserved: tuple[str, ...] = field(default_factory=tuple)
    references: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    provenance_refs: tuple[str, ...] = field(default_factory=tuple)
    response_period: str | None = None
    language: str = "en"
    document_type: str = (
        "Notice of Non-Consent, Conditional Acceptance, and Demand for Resolution"
    )


@dataclass(frozen=True)
class LetterDraftResult:
    document: DocumentDraft
    status: LetterDraftStatus
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    language: str
    references: tuple[str, ...]


class LetterDraftingCapability:
    """Compose structured civic letters without asserting unsupported legal effects."""

    def __init__(self, civic_action: CivicActionCapability) -> None:
        self._civic_action = civic_action

    def create_draft(
        self,
        case_id: str,
        request: LetterDraftRequest,
        *,
        identity,
        document_id: str | None = None,
        date: str | None = None,
    ) -> LetterDraftResult:
        if not request.subject.strip():
            raise ValueError("A subject is required")
        if not request.issue.strip():
            raise ValueError("An issue is required")

        built = self._civic_action.build_document(
            case_id,
            identity=identity,
            document_id=document_id,
            date=date,
        )
        document = replace(
            built.draft,
            document_type=request.document_type,
            subject=request.subject.strip(),
            body=self._compose_body(request),
        )
        return LetterDraftResult(
            document=document,
            status=LetterDraftStatus.DRAFT,
            evidence_refs=tuple(request.evidence_refs),
            provenance_refs=tuple(request.provenance_refs),
            language=request.language,
            references=tuple(request.references),
        )

    @staticmethod
    def mark_reviewed(result: LetterDraftResult) -> LetterDraftResult:
        if result.status is not LetterDraftStatus.DRAFT:
            raise ValueError("Only a draft can transition to reviewed")
        return replace(result, status=LetterDraftStatus.REVIEWED)

    @staticmethod
    def approve(result: LetterDraftResult) -> LetterDraftResult:
        if result.status is not LetterDraftStatus.REVIEWED:
            raise ValueError("Explicit review is required before approval")
        return replace(result, status=LetterDraftStatus.APPROVED)

    @staticmethod
    def require_approved(result: LetterDraftResult) -> DocumentDraft:
        if result.status is not LetterDraftStatus.APPROVED:
            raise PermissionError("Explicit citizen approval is required")
        return result.document

    @staticmethod
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
        if request.response_period:
            sections.extend(["", f"RESPONSE PERIOD: {request.response_period}"])
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
