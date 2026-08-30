"""Shared external-data pipeline with explicit provenance/freshness gates."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from src.core.contracts.external_data_pipeline import (
    ExternalSourceEnvelope,
    FreshnessStatus,
    NormalizedExternalRecord,
)


class SharedExternalDataPipeline:
    def __init__(self, *, freshness_seconds: int = 86400):
        if freshness_seconds < 0:
            raise ValueError("freshness_seconds must be non-negative")
        self.freshness_seconds = freshness_seconds

    def normalize(
        self,
        envelope: ExternalSourceEnvelope,
        records: list[Mapping[str, Any]],
        *,
        record_id_field: str = "record_id",
        validator: Callable[[Mapping[str, Any]], bool] | None = None,
    ) -> tuple[NormalizedExternalRecord, ...]:
        retrieved = datetime.fromisoformat(envelope.retrieved_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age = max(0.0, (now - retrieved).total_seconds())
        freshness = FreshnessStatus.CURRENT if age <= self.freshness_seconds else FreshnessStatus.STALE
        normalized: list[NormalizedExternalRecord] = []
        for item in records:
            if record_id_field not in item:
                raise ValueError(f"missing {record_id_field}")
            valid = validator(item) if validator else True
            normalized.append(
                NormalizedExternalRecord(
                    provider_id=envelope.provider_id,
                    dataset_id=envelope.dataset_id,
                    record_id=str(item[record_id_field]),
                    data=dict(item),
                    source_url=envelope.source_url,
                    retrieved_at=envelope.retrieved_at,
                    licence=envelope.licence,
                    freshness=freshness,
                    provenance_verified=valid,
                )
            )
        return tuple(normalized)
