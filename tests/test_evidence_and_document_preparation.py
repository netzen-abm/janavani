from src.core.capabilities.evidence_case_service import EvidenceReference, SharedEvidenceCaseService
from src.core.capabilities.document_preparation import SharedDocumentPreparation
from src.core.contracts.case import AuthorityReference, Case, VerificationStatus


def verified_case():
    return Case(
        case_id="case-1",
        issue_text="The road is broken",
        category="road",
        authority=AuthorityReference(
            authority_id="auth-1",
            name="Local Authority",
            location="Ward 1",
            verification=VerificationStatus.VERIFIED,
        ),
    )


def test_evidence_is_attached_by_reference_only():
    case = verified_case()
    evidence = EvidenceReference("ev-1", "photo", local=True, sensitive=True)
    SharedEvidenceCaseService().attach(case, evidence)
    assert case.evidence_refs == ["ev-1"]
    assert "raw_content" not in case.metadata


def test_document_requires_verified_authority():
    case = Case(case_id="case-2", issue_text="Broken road")
    try:
        SharedDocumentPreparation().prepare(case, to_name="Authority", to_address="Address")
    except ValueError as exc:
        assert "verified authority" in str(exc)
    else:
        raise AssertionError("unverified authority must not produce a document")


def test_document_is_editable_and_not_submitted():
    draft = SharedDocumentPreparation().prepare(
        verified_case(),
        to_name="Local Authority",
        to_address="Office Address",
        to_email="authority@example.gov",
        cc_name="Citizen Copy",
        cc_address="Citizen Address",
        cc_email="citizen@example.com",
    )
    assert draft.editable is True
    assert draft.submission_enabled is False
    assert draft.source_case_id == "case-1"
