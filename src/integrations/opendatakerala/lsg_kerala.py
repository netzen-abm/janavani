"""Adapter for OpenDataKerala's Kerala LSG public dataset.

This adapter deliberately treats the dataset as geographic/contextual input.
Current legal responsibility must be established separately from authoritative
administrative/legal sources.
"""

from __future__ import annotations

from typing import Any

from src.core.capabilities.external_public_data_provider import ExternalPublicDataProvider
from src.core.contracts.external_public_data import ExternalDataRecord


class OpenDataKeralaLSGProvider(ExternalPublicDataProvider):
    provider_id = "opendatakerala.lsg-kerala-data"
    dataset_id = "kerala_lsg_data"
    source_url = "https://github.com/opendatakerala/lsg-kerala-data"
    licence = "OpenStreetMap ODbL; verify dataset-specific terms before redistribution"

    def search(self, query: dict[str, Any]) -> tuple[ExternalDataRecord, ...]:
        """Translate an upstream response into JanaVani's neutral record contract.

        Network retrieval is intentionally outside this adapter. A fetch layer
        should retrieve and validate upstream data, then pass normalized records
        here. This prevents provider-specific HTTP logic from leaking into core.
        """
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
