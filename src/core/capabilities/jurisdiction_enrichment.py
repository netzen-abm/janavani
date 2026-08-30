"""Channel-neutral jurisdiction enrichment from verified external context."""

from __future__ import annotations

from src.core.contracts.external_public_data import ExternalDataRecord
from src.core.contracts.jurisdiction_enrichment import EnrichmentConfidence, JurisdictionContext


class SharedJurisdictionEnrichment:
    def enrich(self, records: tuple[ExternalDataRecord, ...]) -> JurisdictionContext:
        district = local_body = local_body_type = constituency = road_reference = None
        source_ids: list[str] = []
        confidence = EnrichmentConfidence.UNKNOWN
        for record in records:
            if not record.usable_as_context:
                continue
            data = record.data
            district = district or data.get("district")
            local_body = local_body or data.get("local_body")
            local_body_type = local_body_type or data.get("local_body_type")
            constituency = constituency or data.get("constituency")
            road_reference = road_reference or data.get("road_reference")
            source_ids.append(f"{record.provider_id}:{record.dataset_id}:{record.record_id}")
            if record.usable_as_authority:
                confidence = EnrichmentConfidence.VERIFIED
            elif confidence == EnrichmentConfidence.UNKNOWN:
                confidence = EnrichmentConfidence.CANDIDATE
        return JurisdictionContext(
            district=district,
            local_body=local_body,
            local_body_type=local_body_type,
            constituency=constituency,
            road_reference=road_reference,
            source_ids=tuple(source_ids),
            confidence=confidence,
            notes="Geographic/contextual enrichment only; legal responsibility requires authoritative verification.",
        )
