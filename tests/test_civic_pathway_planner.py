from src.core.capabilities.civic_pathway_planner import SharedCivicPathwayPlanner
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.civic_issue import CivicIssue, IssueDomain, IssueNeed, IssueSignal
from src.core.contracts.civic_pathway import CivicPathway


def authority():
    return AuthorityCandidate("a1", "Verified Authority", "department", "IN-KL", "verified", ("official-1",), AuthorityStatus.VERIFIED)


def test_unverified_procedure_does_not_select_pathway():
    issue = CivicIssue("road", (IssueSignal(IssueDomain.ROADS, IssueNeed.REMEDY, "roads", .9),))
    result = SharedCivicPathwayPlanner().plan(issue, authority(), procedure_verified=False)
    assert result.pathway == CivicPathway.NEEDS_INFORMATION


def test_remedy_selects_complaint():
    issue = CivicIssue("road", (IssueSignal(IssueDomain.ROADS, IssueNeed.REMEDY, "roads", .9),))
    result = SharedCivicPathwayPlanner().plan(issue, authority(), procedure_verified=True)
    assert result.pathway == CivicPathway.COMPLAINT
    assert result.requires_user_confirmation is True


def test_information_selects_rti():
    issue = CivicIssue("records", (IssueSignal(IssueDomain.RTI_INFORMATION, IssueNeed.INFORMATION, "information", .9),))
    result = SharedCivicPathwayPlanner().plan(issue, authority(), procedure_verified=True)
    assert result.pathway == CivicPathway.RTI
