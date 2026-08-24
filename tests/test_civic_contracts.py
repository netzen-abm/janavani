from src.core.civic_authority import AuthorityCandidate, AuthorityConfidence, resolve_authority
from src.core.civic_document import CivicDocument, DocumentStatus, PartyRef
from src.core.civic_evidence import EvidenceObject, EvidenceStatus, validate_evidence


def test_authority_does_not_select_ambiguous_candidates():
    result = resolve_authority(
        "case-1",
        [
            AuthorityCandidate("office-a", confidence=AuthorityConfidence.VERIFIED),
            AuthorityCandidate("office-b", confidence=AuthorityConfidence.VERIFIED),
        ],
    )
    assert result.selected_office_id is None
    assert not result.verified


def test_authority_selects_single_verified_candidate():
    result = resolve_authority(
        "case-1",
        [AuthorityCandidate("office-a", confidence=AuthorityConfidence.VERIFIED)],
    )
    assert result.selected_office_id == "office-a"
    assert result.verified


def test_active_evidence_requires_policy_and_integrity():
    validate_evidence(
        EvidenceObject(
            evidence_id="ev-1",
            storage_ref="store://ev-1",
            sha256="a" * 64,
            evidence_type="document",
            access_policy_ref="private-case",
        )
    )


def test_document_requires_explicit_user_approval_before_export():
    doc = CivicDocument(
        document_id="doc-1",
        document_type="complaint",
        title="Complaint",
        language="en",
        to_party=PartyRef("OFFICE", "Example Office"),
        subject="Issue",
        body="Details",
    )
    assert doc.status is DocumentStatus.DRAFT
    try:
        doc.export()
    except ValueError:
        pass
    else:
        raise AssertionError("draft document must not export")

    doc.approve()
    doc.export()
    assert doc.status is DocumentStatus.EXPORTED
