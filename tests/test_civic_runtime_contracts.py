from src.core.civic_authority import AuthorityCandidate, AuthorityConfidence, resolve_authority
from src.core.civic_case import CaseStatus, CaseType, CivicCase
from src.core.civic_document import CivicDocument, DocumentStatus, PartyRef
from src.core.civic_evidence import EvidenceObject, EvidenceStatus, validate_evidence


def test_civic_case_requires_consent_before_ready_and_never_implies_ack():
    case = CivicCase("case-1", CaseType.COMPLAINT, "Road", "Broken road")
    try:
        case.mark_ready(event_id="ready-1", occurred_at="test")
    except PermissionError:
        pass
    else:
        raise AssertionError("consent must be required")

    case.consent_refs.append("consent-1")
    case.mark_ready(event_id="ready-2", occurred_at="test")
    case.submit(event_id="submit-1", occurred_at="test")
    assert case.status is CaseStatus.SUBMITTED


def test_ambiguous_verified_authority_is_not_selected():
    result = resolve_authority("case-1", [
        AuthorityCandidate("office-a", confidence=AuthorityConfidence.VERIFIED),
        AuthorityCandidate("office-b", confidence=AuthorityConfidence.VERIFIED),
    ])
    assert result.selected_office_id is None
    assert not result.verified


def test_active_evidence_requires_integrity_and_access_policy():
    validate_evidence(EvidenceObject(
        evidence_id="ev-1",
        storage_ref="store://ev-1",
        sha256="a" * 64,
        evidence_type="document",
        access_policy_ref="private-case",
        status=EvidenceStatus.ACTIVE,
    ))


def test_document_cannot_export_before_user_approval():
    document = CivicDocument(
        document_id="doc-1",
        document_type="complaint",
        title="Complaint",
        language="en",
        to_party=PartyRef("OFFICE", "Example Office"),
        subject="Issue",
        body="Details",
    )
    assert document.status is DocumentStatus.DRAFT
    try:
        document.export()
    except ValueError:
        pass
    else:
        raise AssertionError("draft document must not export")
    document.approve()
    document.export()
    assert document.status is DocumentStatus.EXPORTED
