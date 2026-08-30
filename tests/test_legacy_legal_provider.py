from src.core.capabilities.legal_brain_provider import LegacyLegalBrainProvider
from src.core.capabilities.legal_public_source import LegalPublicSourceCapability


def test_legacy_match_is_not_auto_verified():
    result = list(LegacyLegalBrainProvider().search("ration denied"))
    assert result
    assert result[0].verification.value == "unverified"


def test_legacy_unknown_issue_returns_no_record():
    result = list(LegacyLegalBrainProvider().search("completely unknown issue"))
    assert result == []


def test_shared_capability_does_not_promote_legacy_record():
    result = LegalPublicSourceCapability(LegacyLegalBrainProvider()).find("ration denied")
    assert result.found is False
    assert result.sources == ()
