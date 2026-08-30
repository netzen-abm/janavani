from src.core.capabilities.issue_understanding import IssueUnderstanding
from src.core.capabilities.issue_understanding_service import SharedIssueUnderstandingService


class FakeProvider:
    def understand(self, issue_text):
        return IssueUnderstanding(
            category="road",
            department="local_government",
            confidence=0.9,
            source="rule_based",
        )


def test_shared_service_normalizes_input_and_preserves_provider_result():
    service = SharedIssueUnderstandingService(FakeProvider(), "test")
    result = service.understand("  Road is broken  ", language="ml")
    assert result.understanding.category == "road"
    assert result.understanding.department == "local_government"
    assert result.language == "ml"
    assert result.provider == "test"


def test_shared_service_rejects_empty_issue():
    service = SharedIssueUnderstandingService(FakeProvider())
    try:
        service.understand("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass
