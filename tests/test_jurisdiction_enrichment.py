from src.core.capabilities.jurisdiction_enrichment import SharedJurisdictionEnrichment
from src.core.contracts.external_public_data import ExternalDataRecord, ProviderVerificationStatus
from src.core.contracts.jurisdiction_enrichment import EnrichmentConfidence


def record(status, data):
    return ExternalDataRecord(
        provider_id="provider", dataset_id="dataset", record_id="1",
        jurisdiction="IN-KL", data=data, source_url="https://example.gov.in/data",
        verification=status,
    )


def test_context_from_current_unverified_data_is_candidate():
    context = SharedJurisdictionEnrichment().enrich((record(ProviderVerificationStatus.UNVERIFIED, {"district": "Ernakulam", "local_body": "Kochi"}),))
    assert context.district == "Ernakulam"
    assert context.local_body == "Kochi"
    assert context.confidence == EnrichmentConfidence.CANDIDATE


def test_stale_data_is_ignored():
    context = SharedJurisdictionEnrichment().enrich((record(ProviderVerificationStatus.STALE, {"district": "Old"}),))
    assert context.district is None
    assert context.confidence == EnrichmentConfidence.UNKNOWN


def test_verified_data_can_produce_verified_context():
    context = SharedJurisdictionEnrichment().enrich((record(ProviderVerificationStatus.VERIFIED, {"constituency": "Example"}),))
    assert context.constituency == "Example"
    assert context.confidence == EnrichmentConfidence.VERIFIED
