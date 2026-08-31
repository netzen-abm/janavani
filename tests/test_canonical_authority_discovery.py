from types import SimpleNamespace

from src.core.capabilities.canonical_authority_discovery import CanonicalAuthorityDiscoveryGateway
from src.core.contracts.case import AuthorityReference, VerificationStatus
from src.core.contracts.authority_discovery import AuthorityStatus


class Provider:
    def __init__(self, candidates):
        self.candidates = candidates

    def discover(self, issue, *, jurisdiction=None, location=None):
        return self.candidates


def candidate(status=VerificationStatus.UNKNOWN, source="official"):
    return SimpleNamespace(
        authority=AuthorityReference("a1", "Authority", "Kochi", source, status),
        confidence=.8,
        rationale="provider result",
        source="legacy-provider",
    )


def test_gateway_translates_legacy_candidate():
    result = CanonicalAuthorityDiscoveryGateway(Provider([candidate()])).discover(object())
    assert result[0].authority_id == "a1"
    assert result[0].status == AuthorityStatus.CANDIDATE


def test_verified_filter_requires_status_and_provenance():
    verified = candidate(VerificationStatus.VERIFIED, "official-source")
    result = CanonicalAuthorityDiscoveryGateway(Provider([verified])).discover(object())
    assert len(CanonicalAuthorityDiscoveryGateway.verified(result)) == 1

    no_source = candidate(VerificationStatus.VERIFIED, "system")
    result = CanonicalAuthorityDiscoveryGateway(Provider([no_source])).discover(object())
    assert len(CanonicalAuthorityDiscoveryGateway.verified(result)) == 0
