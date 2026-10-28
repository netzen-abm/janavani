"""Versioned, content-free civic document templates.

Templates define reusable structure and guidance only. Citizen values belong in a
draft and must never be added to this catalogue.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateSection:
    """One named slot in a reusable document layout; never a citizen value."""

    field_name: str
    heading: str


@dataclass(frozen=True, slots=True)
class CivicDocumentTemplate:
    """Versioned structural model for deterministic civic-document drafting."""

    template_id: str
    version: int
    title: str
    document_type: str
    purpose: str
    jurisdiction_scope: str
    language: str
    compatible_case_types: tuple[str, ...]
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    sections: tuple[TemplateSection, ...]
    introduction: str
    provenance: str = "Janavani structural model; verify all legal citations and procedures."
    review_status: str = "structural-only"


_COMMON_SECTIONS = (
    TemplateSection("issue", "Matter described by the citizen"),
    TemplateSection("proposal_or_notice", "Proposal or notice"),
    TemplateSection("part_i_interrogatories", "Questions requiring a response"),
    TemplateSection("legal_framework", "Legal or policy framework supplied for review"),
    TemplateSection("requested_conditions", "Requested conditions"),
    TemplateSection("requested_documents", "Records or documents requested"),
    TemplateSection("remedies_reserved", "Requested remedies and rights reserved"),
    TemplateSection("references", "References supplied"),
    TemplateSection("evidence_refs", "Evidence references"),
    TemplateSection("provenance_refs", "Source and provenance references"),
    TemplateSection("response_period", "Requested response period"),
    TemplateSection("deadline_date", "Requested deadline"),
    TemplateSection("jurisdiction", "Jurisdiction stated by the citizen"),
)

_TEMPLATES = (
    CivicDocumentTemplate(
        template_id="complaint.general",
        version=1,
        title="Civic complaint — request for examination and corrective action",
        document_type="Civic complaint",
        purpose="Ask a competent public authority to examine a reported issue and respond.",
        jurisdiction_scope="India; confirm the responsible Central, State or local authority.",
        language="en",
        compatible_case_types=("complaint", "corruption", "misbehaviour", "other"),
        required_fields=("subject", "issue"),
        optional_fields=("jurisdiction", "requested_conditions", "evidence_refs", "references"),
        sections=_COMMON_SECTIONS,
        introduction=(
            "This is a draft complaint based on the citizen's account. It requests "
            "verification and any corrective action warranted by established facts."
        ),
    ),
    CivicDocumentTemplate(
        template_id="grievance.service",
        version=1,
        title="Public-service grievance — request for review and response",
        document_type="Public-service grievance",
        purpose="Ask an authority to review a service deficiency, delay or unresolved request.",
        jurisdiction_scope="India; confirm the applicable department and grievance procedure.",
        language="en",
        compatible_case_types=("grievance", "complaint", "other"),
        required_fields=("subject", "issue"),
        optional_fields=("jurisdiction", "references", "requested_conditions", "response_period"),
        sections=_COMMON_SECTIONS,
        introduction=(
            "This is a draft grievance. The described events are the citizen's account "
            "and should be checked by the responsible office."
        ),
    ),
    CivicDocumentTemplate(
        template_id="rti.records",
        version=1,
        title="RTI application — request for existing records",
        document_type="RTI application draft",
        purpose="Request existing records or information held by a public authority.",
        jurisdiction_scope="India; confirm Central/State RTI rules, fee and correct PIO.",
        language="en",
        compatible_case_types=("rti",),
        required_fields=("subject", "issue", "requested_documents", "jurisdiction"),
        optional_fields=("references", "response_period", "deadline_date"),
        sections=(
            TemplateSection("issue", "Context for the records request"),
            TemplateSection("requested_documents", "Existing records requested"),
            TemplateSection("references", "Reference numbers or public sources"),
            TemplateSection("jurisdiction", "Public authority and jurisdiction"),
        ),
        introduction=(
            "This draft requests existing records or information that may be held by "
            "a public authority. It is not a request for a newly created explanation, "
            "finding or grievance remedy. Confirm the applicable RTI procedure before use."
        ),
    ),
    CivicDocumentTemplate(
        template_id="representation.general",
        version=1,
        title="Citizen representation — evidence-backed request for consideration",
        document_type="Citizen representation",
        purpose="Record a citizen position and request consideration and a written response.",
        jurisdiction_scope="India; verify the authority's mandate and relevant procedure.",
        language="en",
        compatible_case_types=("representation", "objection", "non_consent", "other"),
        required_fields=("subject", "issue"),
        optional_fields=("legal_framework", "references", "requested_conditions", "response_period"),
        sections=_COMMON_SECTIONS,
        introduction=(
            "This draft records the citizen's stated position and requests consideration. "
            "Statements about legal effect remain unverified positions unless supported "
            "by applicable law and facts."
        ),
    ),
    CivicDocumentTemplate(
        template_id="petition.general",
        version=1,
        title="Petition — request for consideration by a competent authority",
        document_type="Petition draft",
        purpose="Present a documented request for consideration or action by a competent body.",
        jurisdiction_scope="India; verify whether a prescribed form or procedure applies.",
        language="en",
        compatible_case_types=("petition", "appeal", "representation"),
        required_fields=("subject", "issue"),
        optional_fields=("references", "requested_conditions", "remedies_reserved", "evidence_refs"),
        sections=_COMMON_SECTIONS,
        introduction=(
            "This is a structured petition draft. Confirm the recipient's jurisdiction, "
            "filing requirements, facts and supporting material before submission."
        ),
    ),
)


class TemplateNotFoundError(LookupError): """Unknown template ID/version."""


def list_templates(*, language: str | None = None) -> tuple[CivicDocumentTemplate, ...]:
    """Return immutable catalogue definitions, optionally filtered by language."""
    templates = _TEMPLATES
    if language is not None:
        normalized = language.strip().lower()
        templates = tuple(item for item in templates if item.language == normalized)
    return templates


def get_template(
    template_id: str,
    *,
    version: int | None = None,
    language: str = "en",
) -> CivicDocumentTemplate:
    """Resolve an approved version. Unknown IDs/versions fail closed."""
    key = template_id.strip().lower()
    locale = language.strip().lower()
    matches = [
        item for item in _TEMPLATES
        if item.template_id == key and item.language == locale
        and (version is None or item.version == version)
    ]
    if not matches:
        raise TemplateNotFoundError(f"Unsupported civic document template: {key}")
    return max(matches, key=lambda item: item.version)
