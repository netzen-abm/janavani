"""Adapter for OpenDataKerala's Kerala roads dataset."""

from __future__ import annotations

from typing import Any

from src.core.capabilities.external_public_data_provider import ExternalPublicDataProvider
from src.core.contracts.external_public_data import ExternalDataRecord


class OpenDataKeralaRoadsProvider(ExternalPublicDataProvider):
    provider_id = "opendatakerala.roads-kerala"
    dataset_id = "kerala_mdr_roads"
    source_url = "https://github.com/opendatakerala/roads-Kerala"
    licence = "Verify repository/dataset licence before redistribution"

    def search(self, query: dict[str, Any]) -> tuple[ExternalDataRecord, ...]:
        records = query.get("records", ())
        return tuple(
            ExternalDataRecord(
                provider_id=self.provider_id,
                dataset_id=self.dataset_id,
                record_id=str(item["record_id"]),
                jurisdiction=item.get("jurisdiction"),
                data=item.get("data", {}),
                source_url=item.get("source_url", self.source_url),
                licence=item.get("licence", self.licence),
                retrieved_at=item.get("retrieved_at"),
                verification=item.get("verification", "unverified"),
            )
            for item in records
        )
