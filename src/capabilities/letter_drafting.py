"""Canonical, surface-neutral civic letter drafting capability.

Letter composition owns only the structured content/template boundary. Persistence,
review state, approval and submission remain with their canonical owners.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.documents.document_contract import DocumentDraft
from src.identity.context import IdentityContext
from src.capabilities.letter_body import compose_letter_body, compose_template_body
from src.documents.template_catalogue import get_template


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
    deadline_date: str | None = None
    jurisdiction: str | None = None
    language: str = "en"
    document_type: str = (
        "Notice of Non-Consent, Conditional Acceptance, and Demand for Resolution"
    )
    template_id: str | None = None
    template_version: int | None = None


@dataclass(frozen=True)
class LetterDraftResult:
    """Persisted, reviewable document plus trace references.

    Review and approval are intentionally not represented as a second state
    machine here. DocumentReviewCapability and the Case lifecycle are canonical.
    """

    document: DocumentDraft
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    language: str
    references: tuple[str, ...]
    template_id: str | None = None
    template_version: int | None = None


class LetterDraftingCapability:
    """Compose structured civic letters and hand them to canonical document review."""

    def __init__(
        self,
        civic_action: CivicActionCapability,
        document_review: DocumentReviewCapability,
    ) -> None:
        self._civic_action = civic_action
        self._document_review = document_review

    def create_draft(
        self,
        case_id: str,
        request: LetterDraftRequest,
        *,
        identity: IdentityContext,
        document_id: str | None = None,
        date: str | None = None,
    ) -> LetterDraftResult:
        if not request.subject.strip():
            raise ValueError("A subject is required")
        if not request.issue.strip():
            raise ValueError("An issue is required")

        template = None
        if request.template_id is not None:
            template = get_template(
                request.template_id,
                version=request.template_version,
                language=request.language,
            )
        elif request.template_version is not None:
            raise ValueError("A template ID is required when a template version is supplied")

        built = self._civic_action.build_document(
            case_id,
            identity=identity,
            document_id=document_id,
            date=date,
        )
        self._validate_request(request, built.case, template=template)
        document = replace(
            built.draft,
            document_type=template.document_type if template else request.document_type,
            subject=request.subject.strip(),
            body=compose_template_body(request, template) if template else compose_letter_body(request),
            template_id=template.template_id if template else None,
            template_version=template.version if template else None,
        )
        persisted = self._document_review.save_draft(document, identity=identity)
        return LetterDraftResult(
            document=persisted,
            evidence_refs=tuple(request.evidence_refs),
            provenance_refs=tuple(request.provenance_refs),
            language=request.language,
            references=tuple(request.references),
            template_id=template.template_id if template else None,
            template_version=template.version if template else None,
        )

    @staticmethod
    def _validate_request(request: LetterDraftRequest, case, *, template=None) -> None:
        """Fail closed on unsupported placeholders and unbound evidence references."""
        if template is not None:
            case_type = getattr(case.case_type, "value", case.case_type)
            if case_type not in template.compatible_case_types:
                raise ValueError(
                    f"Template {template.template_id} is not compatible with case type {case_type}"
                )
            missing = []
            for field_name in template.required_fields:
                value = getattr(request, field_name, None)
                if not value or (isinstance(value, str) and not value.strip()):
                    missing.append(field_name)
            if missing:
                raise ValueError("Template requires: " + ", ".join(missing))
        if request.legal_framework and not (request.jurisdiction or "").strip():
            raise ValueError("Jurisdiction is required when legal framework is supplied")
        if request.response_period is not None and not request.response_period.strip():
            raise ValueError("Response period cannot be blank")
        if request.deadline_date is not None and not request.deadline_date.strip():
            raise ValueError("Deadline date cannot be blank")
        for field_name, values in (
            ("evidence_refs", request.evidence_refs),
            ("provenance_refs", request.provenance_refs),
        ):
            if any(not value.strip() for value in values):
                raise ValueError(f"{field_name} cannot contain blank references")
        missing_evidence = [
            ref for ref in request.evidence_refs if ref not in case.evidence_refs
        ]
        if missing_evidence:
            raise ValueError(
                "Letter evidence references are not attached to the case: "
                + ", ".join(missing_evidence)
            )
        content = "\n".join((request.subject, request.issue, request.proposal_or_notice))
        forbidden_placeholders = ("[Insert ", "{{", "Dear X", "<recipient>")
        if any(token.lower() in content.lower() for token in forbidden_placeholders):
            raise ValueError("Draft contains unresolved placeholder text")

