"""Curated, source-controlled structural definitions for civic documents.

Only generic headings and reviewed starter wording belong here. Never put citizen
names, contact details, issue narratives, case IDs, evidence or completed letters
into this source-controlled catalogue.
"""
from src.documents.template_models import CivicDocumentTemplate, TemplateSection
from src.documents.template_administrative import _ADMINISTRATIVE_EVIDENCE_DEMAND
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
        purpose="Ask a competent public authority to examine a reported issue and consider corrective action.",
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
            TemplateSection("proposal_or_notice", "Optional wording for review (not a new information demand)"),
            TemplateSection("requested_documents", "Existing records requested"),
            TemplateSection("references", "Reference numbers or public sources"), TemplateSection("jurisdiction", "Public authority and jurisdiction"),
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
    _ADMINISTRATIVE_EVIDENCE_DEMAND,
)