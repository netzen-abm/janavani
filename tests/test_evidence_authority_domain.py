from datetime import timezone

from src.domain.authority import AuthorityReference
from src.domain.evidence import Evidence, EvidenceKind, VerificationStatus


def test_evidence_defaults_to_unverified_and_has_utc_timestamp():
    evidence = Evidence(kind=EvidenceKind.IMAGE, title="Road damage")

    assert evidence.evidence_id
    assert evidence.verification_status is VerificationStatus.UNVERIFIED
    assert evidence.created_at.tzinfo is timezone.utc


def test_evidence_verification_is_explicit():
    evidence = Evidence(title="Official response")

    evidence.mark_verified(notes="Verified against source record")

    assert evidence.verification_status is VerificationStatus.VERIFIED
    assert evidence.verification_notes == "Verified against source record"


def test_authority_reference_does_not_claim_unverified_source():
    authority = AuthorityReference(name="Municipal Office", jurisdiction="Ward 1")

    assert authority.authority_id
    assert authority.source_verified is False
    assert authority.official_source_ref is None
    assert authority.retrieved_at.tzinfo is timezone.utc
