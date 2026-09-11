"""Reference obligation resolver backed by explicit source records."""
from __future__ import annotations

from src.core.obligation import (
    ObligationBasis,
    ObligationConfidence,
    ObligationObservation,
    ObligationResolution,
    ObligationResolver,
)


class AuthorityBackedObligationResolver(ObligationResolver):
    """Conservative reference adapter for authority-scoped obligation records.

    The adapter intentionally requires an explicit obligation source. It never
    infers that an authority breached a duty and never converts an observation
    into a legal finding.
    """

    def __init__(self, records: dict[str, list[dict[str, object]]]) -> None:
        self._records = records

    def resolve(self, observation: ObligationObservation) -> ObligationResolution:
        matches = self._records.get(observation.authority_id, [])
        links = []
        for record in matches:
            obligation_id = str(record.get("obligation_id", "")).strip()
            title = str(record.get("title", "")).strip()
            description = str(record.get("description", "")).strip()
            source_refs = tuple(str(ref).strip() for ref in record.get("source_refs", ()) if str(ref).strip())
            if not obligation_id or not title or not description or not source_refs:
                continue
            verified = bool(record.get("verified", False))
            links.append(
                {
                    "obligation_id": obligation_id,
                    "title": title,
                    "description": description,
                    "confidence": ObligationConfidence.MATCHED_RECORD if verified else ObligationConfidence.VERIFICATION_REQUIRED,
                    "basis": ObligationBasis(str(record.get("basis", ObligationBasis.OFFICIAL_RECORD.value))),
                    "source_refs": source_refs,
                    "authority_id": observation.authority_id,
                    "applicability": str(record.get("applicability", "")).strip() or None,
                    "remedy": str(record.get("remedy", "")).strip() or None,
                    "verification_required": not verified,
                    "notes": "Source-backed obligation candidate; applicability and breach remain separately reviewable.",
                }
            )

        from src.core.obligation import ObligationLink

        resolution = ObligationResolution(
            resolution_id=f"obl-{observation.observation_id}",
            observation_id=observation.observation_id,
            links=tuple(ObligationLink(**link) for link in links),
        )
        resolution.require_source()
        return resolution
