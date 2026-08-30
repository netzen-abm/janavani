from dataclasses import dataclass

from src.core.capabilities.civic_case_orchestrator import SharedCivicCaseOrchestrator
from src.core.contracts.case import AuthorityReference, VerificationStatus


@dataclass
class Understanding:
    category: str = "public_service"
    department: str = "panchayat"


class FakeIssueUnderstanding:
    def understand(self, text, language):
        return Understanding()


@dataclass
class Candidate:
    authority: AuthorityReference


class FakeAuthorityDiscovery:
    def discover(self, understanding, *, jurisdiction=None, location=None):
        return [Candidate(AuthorityReference("a1", "Panchayat", location, "verified", VerificationStatus.VERIFIED))]


def test_orchestrator_builds_shared_case_plan():
    service = SharedCivicCaseOrchestrator(FakeIssueUnderstanding(), FakeAuthorityDiscovery())
    result = service.start("The panchayat has not repaired the road", location="Kochi")
    assert result.case.issue_text.startswith("The panchayat")
    assert result.case.authority is not None
    assert result.action_plan.recommendations
    assert result.action_graph.nodes


def test_orchestrator_rejects_empty_narrative():
    service = SharedCivicCaseOrchestrator(FakeIssueUnderstanding(), FakeAuthorityDiscovery())
    try:
        service.start("   ")
    except ValueError as exc:
        assert "issue_text" in str(exc)
    else:
        raise AssertionError("empty narrative should fail")
