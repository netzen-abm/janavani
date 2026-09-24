from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.letter_drafting import (
    LetterDraftRequest,
    LetterDraftStatus,
    LetterDraftingCapability,
)
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def test_letter_draft_requires_review_before_approval() -> None:
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-letter",
            name="Office",
            authority_type="office",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(
                name="Authority",
                address="Address",
                email="authority@example.test",
                verified=True,
            ),
            verification_status="VERIFIED",
        )
    ])
    identity = IdentityContext(
        principal=Principal(
            principal_id="letter-principal",
            interface="test",
            capabilities=frozenset(
                {"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}
            ),
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

    action = CivicActionCapability(
        case_capability=CivicCaseCapability(cases),
        case_repository=cases,
        authority_repository=authorities,
    )
    capability = LetterDraftingCapability(action)

    result = capability.create_draft(
        case.case_id,
        LetterDraftRequest(
            subject="Notice and demand for resolution",
            issue="I do not consent to proceeding without a documented response.",
            legal_framework=("Article 21", "Precautionary Principle"),
            requested_conditions=("Provide adequate public participation.",),
            evidence_refs=("evidence-1",),
            provenance_refs=("source-1",),
            response_period="28 days",
        ),
        identity=identity,
        document_id="letter-1",
        date="2026-09-24",
    )

    assert result.status is LetterDraftStatus.DRAFT
    assert "Article 21" in result.document.body
    assert "evidence-1" in result.evidence_refs

    try:
        capability.require_approved(result)
    except PermissionError:
        pass
    else:
        raise AssertionError("Unreviewed draft must not be treated as approved")

    reviewed = capability.mark_reviewed(result)
    approved = capability.approve(reviewed)

    assert approved.status is LetterDraftStatus.APPROVED
    assert capability.require_approved(approved).document_id == "letter-1"
