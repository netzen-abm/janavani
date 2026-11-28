from dataclasses import asdict

import pytest

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.document_review import DocumentReviewCapability, DocumentReviewRequest
from src.capabilities.letter_body import compose_template_body
from src.capabilities.letter_drafting import LetterDraftRequest, LetterDraftingCapability
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.documents.template_catalogue import (
    TemplateNotFoundError,
    get_template,
    list_templates,
)
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.document_review import InMemoryDocumentReviewRepository


def _drafting(case_type: CaseType):
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="template-office",
            name="Public Office",
            authority_type="office",
            jurisdiction={"state": "Kerala"},
            primary_contact=AuthorityContact(
                name="Public Information Officer",
                address="Official address",
                verified=True,
            ),
            verification_status="VERIFIED",
        )
    ])
    identity = IdentityContext(
        principal=Principal(
            principal_id="template-test-owner",
            interface="test",
            capabilities=frozenset({
                "JNV-CIVIC-COMPLAINT", "case:write", "case:review", "document:review"
            }),
        )
    )
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=case_type,
            subject="Public road maintenance",
            narrative="Please examine the reported road condition.",
            related_office_id="template-office",
        ),
        identity=identity,
        source_channel="test",
    ).case
    case_capability = CivicCaseCapability(cases)
    action = CivicActionCapability(
        case_capability=case_capability,
        case_repository=cases,
        authority_repository=authorities,
    )
    repository = InMemoryDocumentReviewRepository()
    review = DocumentReviewCapability(repository, case_capability=case_capability)
    return LetterDraftingCapability(action, review), case, identity, review


def test_template_default_items_are_always_immutable_tuples():
    for template in list_templates():
        for section in template.sections:
            assert isinstance(section.default_items, tuple), (
                template.template_id, section.field_name, type(section.default_items).__name__
            )
            assert all(isinstance(item, str) for item in section.default_items)


def test_catalogue_contains_versioned_structural_models_not_citizen_values():
    templates = list_templates(language="en")
    ids = {item.template_id for item in templates}

    assert {
        "complaint.general",
        "grievance.service",
        "rti.records",
        "representation.general",
        "petition.general",
        "administrative.evidence-demand",
    } <= ids
    assert all(item.version >= 1 for item in templates)
    assert all(item.review_status == "structural-only" for item in templates)

    serialized = repr([asdict(item) for item in templates]).casefold()
    assert "phone number" not in serialized
    assert "citizen name" not in serialized
    assert "case id" not in serialized
    assert "raw narrative" not in serialized


def test_unknown_template_or_version_fails_closed():
    with pytest.raises(TemplateNotFoundError):
        get_template("not-a-real-template")
    with pytest.raises(TemplateNotFoundError):
        get_template("rti.records", version=2)


def test_rti_template_drafts_existing_records_and_retains_template_version():
    capability, case, identity, review = _drafting(CaseType.RTI)
    result = capability.create_draft(
        case.case_id,
        LetterDraftRequest(
            subject="Records concerning road maintenance",
            issue="Please identify the records held about the maintenance work.",
            requested_documents=(
                "Copies of existing work orders for the stated period",
                "Copies of existing inspection reports, if held",
            ),
            jurisdiction="Kerala State public authority",
            template_id="rti.records",
            template_version=1,
        ),
        identity=identity,
        document_id="template-rti-1",
        date="2026-10-28",
    )

    assert result.document.document_type == "RTI application draft"
    assert result.document.template_id == "rti.records"
    assert result.document.template_version == 1
    assert "Existing records requested" in result.document.body
    assert "not a request for a newly created explanation" in result.document.body
    assert review.get_owned("template-rti-1", identity=identity) == result.document

    edited = review.edit(
        DocumentReviewRequest(
            document_id="template-rti-1",
            body=result.document.body + "\nCitizen-reviewed correction.",
            reason="Citizen correction",
        ),
        identity=identity,
    )
    assert edited.template_id == "rti.records"
    assert edited.template_version == 1


def test_rti_template_requires_a_record_list_and_jurisdiction():
    capability, case, identity, _review = _drafting(CaseType.RTI)
    with pytest.raises(ValueError, match="Template requires: requested_documents, jurisdiction"):
        capability.create_draft(
            case.case_id,
            LetterDraftRequest(
                subject="Request for records",
                issue="Please provide the existing record.",
                template_id="rti.records",
            ),
            identity=identity,
        )


def test_template_must_match_case_type():
    capability, case, identity, _review = _drafting(CaseType.COMPLAINT)
    with pytest.raises(ValueError, match="not compatible with case type complaint"):
        capability.create_draft(
            case.case_id,
            LetterDraftRequest(
                subject="Request for records",
                issue="Please provide records held about the matter.",
                requested_documents=("Copies of the existing work order",),
                jurisdiction="Kerala",
                template_id="rti.records",
            ),
            identity=identity,
        )


def test_complaint_and_rti_templates_have_distinct_purposes():
    complaint = get_template("complaint.general")
    rti = get_template("rti.records")

    assert "corrective action" in complaint.purpose
    assert "existing records" in rti.purpose
    assert complaint.document_type != rti.document_type
    assert "requested_documents" not in complaint.required_fields
    assert "requested_documents" in rti.required_fields


def test_administrative_evidence_demand_is_content_free_and_renders_reviewed_defaults():
    template = get_template("administrative.evidence-demand")
    structural_text = repr(asdict(template)).casefold()
    assert template.version == 1
    assert template.review_status == "structural-only"
    assert "certified copies" in structural_text
    assert "authority name" not in structural_text
    assert "phone number" not in structural_text
    assert "self-executing instrument" not in structural_text
    assert "tacit agreement" not in structural_text

    body = compose_template_body(
        LetterDraftRequest(
            subject="Reply to sanitation levy notice",
            issue="The notice requests a recurring sanitation levy.",
            jurisdiction="Kerala municipal authority",
            template_id=template.template_id,
            template_version=template.version,
        ),
        template,
    )

    assert "Part I — Foundational and constitutional questions" in body
    assert "Part II — Documents and records requested" in body
    assert "Part III — Rights and remedies reserved" in body
    assert "certified copies" in body
    assert "Date: [Insert date of writing]" in body
    assert "Requested response period: [Insert a requested period" in body
    assert "certified copies in the form prescribed" in body
    assert "Copy to: [Insert relevant oversight authority or local body" in body
    assert "The notice requests a recurring sanitation levy." in body
    assert "Kerala municipal authority" in body
    assert "Complete or remove every bracketed prompt" in body
    assert "Non-response alone is not asserted here to constitute agreement" in body
    assert "Citizen-reviewed" not in body  # no data from a previous citizen draft
