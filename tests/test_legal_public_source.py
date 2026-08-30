import pytest

from src.core.capabilities.legal_public_source import LegalPublicSourceCapability
from src.core.contracts.legal_source import (
    LegalSourceReference,
    SourceVerificationStatus,
)


class FakeProvider:
    def __init__(self, sources):
        self.sources = sources

    def search(self, query, *, jurisdiction=None):
        return self.sources


def test_only_verified_sources_are_returned():
    provider = FakeProvider([
        LegalSourceReference("1", "Verified", verification=SourceVerificationStatus.VERIFIED),
        LegalSourceReference("2", "Pending", verification=SourceVerificationStatus.PENDING),
    ])
    result = LegalPublicSourceCapability(provider).find("RTI", jurisdiction="India")
    assert result.found is True
    assert [s.source_id for s in result.sources] == ["1"]


def test_missing_source_is_explicit_and_not_a_default_law():
    provider = FakeProvider([])
    result = LegalPublicSourceCapability(provider).find("unknown issue")
    assert result.found is False
    assert result.sources == ()
    assert "No verified" in result.message


def test_unverified_only_results_are_not_promoted():
    provider = FakeProvider([
        LegalSourceReference("1", "Unverified", verification=SourceVerificationStatus.UNVERIFIED),
    ])
    result = LegalPublicSourceCapability(provider).find("unknown")
    assert result.found is False
