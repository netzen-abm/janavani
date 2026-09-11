"""Reference responsibility resolver backed by canonical authority records."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.core.authority import AuthorityRepository
from src.core.responsibility import (
    ResolutionBasis,
    ResolutionConfidence,
    ResponsibilityLink,
    ResponsibilityObservation,
    ResponsibilityResolution,
    ResponsibilityResolver,
)


class AuthorityBackedResponsibilityResolver(ResponsibilityResolver):
    """Resolve an observation to traceable authority candidates.

    This adapter performs deterministic record lookup only. It does not infer
    guilt, liability, misconduct, contractual breach, or final responsibility.
    """

    def __init__(self, authority_repository: AuthorityRepository, *, limit: int = 5) -> None:
        if limit < 1:
            raise ValueError("Resolution limit must be positive")
        self._authority_repository = authority_repository
        self._limit = limit

    def resolve(self, observation: ResponsibilityObservation) -> ResponsibilityResolution:
        city = observation.location.get("city", "").strip()
        authority_type = (observation.authority_type_hint or "").strip()
        if not city:
            raise ValueError("Responsibility resolution requires a city")
        if not authority_type:
            raise ValueError("Responsibility resolution requires an authority type hint")

        records = self._authority_repository.search(
            authority_type=authority_type,
            city=city,
            limit=self._limit,
        )
        links = tuple(
            ResponsibilityLink(
                entity_type="authority",
                entity_id=record.authority_id,
                entity_name=record.name,
                confidence=(
                    ResolutionConfidence.MATCHED_RECORD
                    if record.verified
                    else ResolutionConfidence.HIGH_CONFIDENCE
                ),
                basis=ResolutionBasis.OFFICIAL_RECORD,
                source_refs=record.source_refs,
                verification_required=not record.verified,
                notes=(
                    "Matched verified authority record."
                    if record.verified
                    else "Matched authority record; verification remains required."
                ),
            )
            for record in records
        )
        return ResponsibilityResolution(
            resolution_id=f"responsibility-{uuid4().hex}",
            observation_id=observation.observation_id,
            links=links,
            resolved_at=datetime.now(timezone.utc).isoformat(),
        )
