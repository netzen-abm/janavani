from src.core.capabilities.authority_discovery_service import AuthorityCandidate, SharedAuthorityDiscovery
from src.core.capabilities.issue_understanding import IssueUnderstanding
from src.core.contracts.case import AuthorityReference, VerificationStatus


class FakeAuthorityProvider:
    def discover(self, issue, *, jurisdiction=None, location=None):
        return [
            AuthorityCandidate(
                AuthorityReference(name="Road Authority", location=location or "Kochi"),
                confidence=1.4,
                rationale="matched road maintenance",
            ),
            AuthorityCandidate(
                AuthorityReference(name="Citizen Suggested Office", source="citizen_provided"),
                confidence=-0.2,
            ),
        ]


def test_discovery_clamps_confidence_and_preserves_system_source():
    issue = IssueUnderstanding("road", "local government", 0.9)
    results = SharedAuthorityDiscovery(FakeAuthorityProvider()).discover(issue, jurisdiction="Kerala", location="Kochi")
    assert results[0].confidence == 1.0
    assert results[0].authority.verification == VerificationStatus.UNKNOWN


def test_citizen_supplied_authority_is_pending_not_verified():
    issue = IssueUnderstanding("road", "local government")
    results = SharedAuthorityDiscovery(FakeAuthorityProvider()).discover(issue)
    assert results[1].authority.verification == VerificationStatus.PENDING
    assert results[1].authority.source == "citizen_provided"
