from types import SimpleNamespace

from src.core.capabilities.authority_candidate_adapter import canonical_to_legacy, legacy_to_canonical
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.case import AuthorityReference, VerificationStatus


def test_legacy_verified_candidate_maps_to_canonical_verified():
    legacy = SimpleNamespace(
        authority=AuthorityReference(
            authority_id="road-1",
            name="Road Authority",
            location="Kochi",
            source="official-source-1",
            verification=VerificationStatus.VERIFIED,
        ),
        rationale="verified database match",
    )
    result = legacy_to_canonical(legacy)
    assert result.authority_id == "road-1"
    assert result.status == AuthorityStatus.VERIFIED
    assert result.source_ids == ("official-source-1",)


def test_legacy_unverified_candidate_remains_candidate():
    legacy = SimpleNamespace(
        authority=AuthorityReference(name="Citizen Suggested Office", source="citizen_provided"),
        rationale="citizen supplied",
    )
    result = legacy_to_canonical(legacy)
    assert result.status == AuthorityStatus.CANDIDATE
    assert result.source_ids == ("citizen_provided",)


def test_canonical_verified_candidate_maps_to_legacy_verified():
    canonical = AuthorityCandidate(
        authority_id="office-1",
        name="Office",
        authority_type="department",
        jurisdiction="Ernakulam",
        reason="verified procedure source",
        source_ids=("official-source-1",),
        status=AuthorityStatus.VERIFIED,
    )
    result = canonical_to_legacy(canonical)
    assert result.authority.verification == VerificationStatus.VERIFIED
    assert result.authority.source == "official-source-1"
    assert result.confidence == 1.0


def test_canonical_stale_candidate_is_not_verified_for_legacy():
    canonical = AuthorityCandidate(
        authority_id="office-old",
        name="Old Office",
        authority_type="department",
        jurisdiction="Ernakulam",
        reason="stale source",
        status=AuthorityStatus.STALE,
    )
    result = canonical_to_legacy(canonical)
    assert result.authority.verification == VerificationStatus.REJECTED
    assert result.confidence == 0.0
