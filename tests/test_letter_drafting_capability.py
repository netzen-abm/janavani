from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.document_review import DocumentReviewCapability, DocumentReviewRequest
from src.capabilities.letter_drafting import LetterDraftRequest, LetterDraftingCapability
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.document_review import InMemoryDocumentReviewRepository


def test_letter_draft_persists_into_canonical_review_boundary() -> None:
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-letter",
            name="Office",
            authority_type="office",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(
                name="Authority", address="Address",
                email="authority@example.test", verified=True,
            ),
            verification_status="VERIFIED",
        )
    ])
    identity = IdentityContext(
        principal=Principal(
            principal_id="letter-principal",
            interface="test",
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}),
        )
    )
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.REPRESENTATION,
            subject="Public consultation",
            narrative="The consultation requires a documented response.",
            related_office_id="office-letter",
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
    review_repository = InMemoryDocumentReviewRepository()
    review = DocumentReviewCapability(review_repository, case_capability=case_capability)
    capability = LetterDraftingCapability(action, review)

    result = capability.create_draft(
        case.case_id,
        LetterDraftRequest(
            subject="Notice and demand for resolution",
            issue="I request a documented response.",
            legal_framework=("Article 21", "Precautionary Principle"),
            evidence_refs=("evidence-1",),
            provenance_refs=("source-1",),
            response_period="28 days",
        ),
        identity=identity,
        document_id="letter-1",
        date="2026-09-24",
    )

    assert review.get_owned("letter-1", identity=identity) == result.document
    assert result.evidence_refs == ("evidence-1",)
    assert result.provenance_refs == ("source-1",)

    edited = review.edit(
        DocumentReviewRequest(
            document_id="letter-1",
            body="Citizen-reviewed replacement text.",
            reason="Citizen correction",
        ),
        identity=identity,
    )
    assert edited.body == "Citizen-reviewed replacement text."


def test_letter_drafting_requires_jurisdiction_for_legal_framework() -> None:
    # The existing fixture intentionally does not attach evidence; use a minimal
    # request so this test isolates the jurisdiction gate.
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-jurisdiction",
            name="Office",
            authority_type="office",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(name="Authority", address="Address", verified=True),
            verification_status="VERIFIED",
        )
    ])
    identity = IdentityContext(
        principal=Principal(
            principal_id="jurisdiction-principal",
            interface="test",
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}),
        )
    )
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.REPRESENTATION,
            subject="Consultation",
            narrative="Documented response requested.",
            related_office_id="office-jurisdiction",
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
    review = DocumentReviewCapability(
        InMemoryDocumentReviewRepository(), case_capability=case_capability
    )
    capability = LetterDraftingCapability(action, review)
    import pytest
    with pytest.raises(ValueError, match="Jurisdiction is required"):
        capability.create_draft(
            case.case_id,
            LetterDraftRequest(
                subject="Notice",
                issue="Please respond.",
                legal_framework=("Article 21",),
            ),
            identity=identity,
        )
