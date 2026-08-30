from src.core.capabilities.authority_discovery import SharedAuthorityDiscovery
from src.core.contracts.authority_discovery import AuthorityStatus
from src.core.contracts.civic_issue import CivicIssue, IssueDomain, IssueNeed, IssueSignal
from src.core.contracts.jurisdiction_enrichment import EnrichmentConfidence, JurisdictionContext


def test_road_issue_produces_candidate_not_authority():
    issue = CivicIssue(
        summary="broken road",
        signals=(IssueSignal(IssueDomain.ROADS, IssueNeed.REMEDY, "roads", 0.9),),
    )
    jurisdiction = JurisdictionContext(district="Ernakulam", local_body="Example Municipality", local_body_type="municipality", confidence=EnrichmentConfidence.CANDIDATE)
    result = SharedAuthorityDiscovery().discover(issue, jurisdiction)
    assert result
    assert result[0].status == AuthorityStatus.CANDIDATE


def test_verification_requires_authoritative_sources():
    issue = CivicIssue("broken road", (IssueSignal(IssueDomain.ROADS, IssueNeed.REMEDY, "roads", 0.9),))
    jurisdiction = JurisdictionContext(local_body="Example Municipality")
    candidate = SharedAuthorityDiscovery().discover(issue, jurisdiction)[0]
    try:
        SharedAuthorityDiscovery.verify(candidate, source_ids=())
        assert False, "verification without sources must fail"
    except ValueError:
        pass
