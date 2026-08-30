from src.core.capabilities.authority_discovery_service import AuthorityCandidate, SharedAuthorityDiscovery
from src.core.capabilities.case_orchestrator import SharedCaseOrchestrator
from src.core.capabilities.issue_understanding import IssueUnderstanding, SharedIssueUnderstanding
from src.core.contracts.case import AuthorityReference, VerificationStatus


class IssueProvider:
    def understand(self, issue_text, language="en"):
        return IssueUnderstanding("road", "local_government", 0.95, "rule_based")


class AuthorityProvider:
    def discover(self, issue, *, jurisdiction=None, location=None):
        return [
            AuthorityCandidate(
                AuthorityReference("auth-1", "Local Authority", location, "system", VerificationStatus.VERIFIED),
                0.9,
                "jurisdiction match",
            )
        ]


def test_shared_orchestrator_routes_issue_to_verified_authority():
    orchestrator = SharedCaseOrchestrator(
        SharedIssueUnderstanding(IssueProvider()),
        SharedAuthorityDiscovery(AuthorityProvider()),
    )
    result = orchestrator.start_case("The road is broken", jurisdiction="Kochi", location="Ward 1")
    assert result.case.category == "road"
    assert result.case.department == "local_government"
    assert result.case.authority.verification == VerificationStatus.VERIFIED
    assert result.case.status.value == "review"


def test_citizen_authority_is_always_pending():
    orchestrator = SharedCaseOrchestrator(
        SharedIssueUnderstanding(IssueProvider()),
        SharedAuthorityDiscovery(AuthorityProvider()),
    )
    case = orchestrator.start_case("The road is broken").case
    authority = AuthorityReference(name="Citizen Suggested Office", source="citizen_provided")
    updated = orchestrator.accept_citizen_authority(case, authority)
    assert updated.authority.verification == VerificationStatus.PENDING
