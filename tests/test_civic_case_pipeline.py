from src.core.capabilities.civic_case_pipeline import SharedCivicCasePipeline
from src.core.capabilities.authority_discovery import SharedAuthorityDiscovery
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.civic_pathway import CivicPathway


def verified_authority():
    return AuthorityCandidate(
        authority_id="authority-1",
        name="Verified Municipality",
        authority_type="municipality",
        jurisdiction="Ernakulam",
        reason="authoritatively verified",
        source_ids=("official-authority-source",),
        status=AuthorityStatus.VERIFIED,
        to_address="Verified Municipality Office",
        to_email="office@example.gov.in",
    )


def test_pipeline_stops_at_needs_information_without_verified_authority_or_procedure():
    assessment = SharedCivicCasePipeline().assess(
        "The road near my home is broken",
        jurisdiction=None,
    )
    assert assessment.pathway.pathway == CivicPathway.NEEDS_INFORMATION
    assert assessment.authority_candidates == ()


def test_pipeline_selects_complaint_after_verified_authority_and_procedure():
    assessment = SharedCivicCasePipeline().assess(
        "The road near my home is broken",
        verified_authority=verified_authority(),
        procedure_verified=True,
    )
    assert assessment.pathway.pathway == CivicPathway.COMPLAINT
    assert assessment.pathway.authority_id == "authority-1"


def test_discovery_candidate_is_never_treated_as_verified_authority():
    assessment = SharedCivicCasePipeline().assess(
        "The road near my home is broken",
        jurisdiction=__import__(
            "src.core.contracts.jurisdiction_enrichment", fromlist=["JurisdictionContext"]
        ).JurisdictionContext(local_body="Example Municipality"),
        procedure_verified=True,
    )
    assert assessment.authority_candidates
    assert assessment.authority_candidates[0].status == AuthorityStatus.CANDIDATE
    assert assessment.pathway.pathway == CivicPathway.NEEDS_INFORMATION
