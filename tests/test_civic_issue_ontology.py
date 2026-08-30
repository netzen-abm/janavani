from src.core.capabilities.civic_issue_ontology import SharedCivicIssueOntology
from src.core.contracts.civic_issue import IssueDomain, IssueNeed


def test_road_problem_is_classified_as_remedy():
    issue = SharedCivicIssueOntology().classify("The road is broken and needs repair", location_hint="Kochi")
    assert issue.location_hint == "Kochi"
    assert issue.signals[0].domain == IssueDomain.ROADS
    assert issue.signals[0].need == IssueNeed.REMEDY


def test_information_and_remedy_are_multiple_needs():
    issue = SharedCivicIssueOntology().classify("The road is broken and I need information about the sanctioned amount")
    assert issue.signals[0].domain == IssueDomain.ROADS
    assert issue.signals[0].need == IssueNeed.MULTIPLE


def test_claimed_official_fact_requires_verification():
    issue = SharedCivicIssueOntology().classify("They said the project was sanctioned")
    assert "claimed official decision/rule requires authoritative verification" in issue.facts_requiring_verification
