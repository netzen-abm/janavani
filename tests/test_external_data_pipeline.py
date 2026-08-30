from datetime import datetime, timedelta, timezone

import pytest

from src.core.capabilities.external_data_pipeline import SharedExternalDataPipeline
from src.core.contracts.external_data_pipeline import ExternalSourceEnvelope, FreshnessStatus


def envelope(when: datetime):
    return ExternalSourceEnvelope(
        provider_id="test.provider",
        dataset_id="dataset",
        source_url="https://example.gov.in/data",
        retrieved_at=when.isoformat(),
        raw=None,
        licence="test",
    )


def test_current_data_is_normalized():
    result = SharedExternalDataPipeline(freshness_seconds=3600).normalize(
        envelope(datetime.now(timezone.utc)), [{"record_id": "1", "name": "Kochi"}]
    )
    assert result[0].freshness == FreshnessStatus.CURRENT
    assert result[0].provenance_verified is False


def test_old_data_is_marked_stale():
    old = datetime.now(timezone.utc) - timedelta(days=3)
    result = SharedExternalDataPipeline(freshness_seconds=3600).normalize(
        envelope(old), [{"record_id": "1"}]
    )
    assert result[0].freshness == FreshnessStatus.STALE


def test_record_id_is_required():
    with pytest.raises(ValueError):
        SharedExternalDataPipeline().normalize(envelope(datetime.now(timezone.utc)), [{"name": "missing"}])


def test_validator_controls_provenance_flag():
    result = SharedExternalDataPipeline().normalize(
        envelope(datetime.now(timezone.utc)),
        [{"record_id": "1"}],
        validator=lambda item: True,
    )
    assert result[0].provenance_verified is True
