"""Provider-neutral responsibility resolution contracts.

The resolver connects a civic observation to potentially relevant public records
without turning inference into a finding of guilt, liability, or misconduct.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ResolutionConfidence(str, Enum):
    """Evidence-backed confidence levels for a responsibility match."""

    OBSERVED = "observed"
    HIGH_CONFIDENCE = "high_confidence"
    MATCHED_RECORD = "matched_record"
    PROBABLE = "probable"
    VERIFICATION_REQUIRED = "verification_required"


class ResolutionBasis(str, Enum):
    """What kind of fact supports a resolution."""

    OBSERVATION = "observation"
    JURISDICTION = "jurisdiction"
    OFFICIAL_RECORD = "official_record"
    CONTRACT = "contract"
    WARRANTY = "warranty"
    USER_PROVIDED = "user_provided"


@dataclass(frozen=True)
class ResponsibilityObservation:
    """A citizen/system observation used as input to responsibility resolution."""

    observation_id: str
    description: str
    location: dict[str, str] = field(default_factory=dict)
    asset_ref: str | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResponsibilityLink:
    """A traceable candidate relationship between an observation and an entity."""

    entity_type: str
    entity_id: str
    entity_name: str
    confidence: ResolutionConfidence
    basis: ResolutionBasis
    source_refs: tuple[str, ...] = field(default_factory=tuple)
    verification_required: bool = True
    notes: str | None = None


@dataclass(frozen=True)
class ResponsibilityResolution:
    """Immutable resolution result; inference never becomes authoritative fact."""

    resolution_id: str
    observation_id: str
    links: tuple[ResponsibilityLink, ...] = field(default_factory=tuple)
    resolved_at: str | None = None

    @property
    def has_verified_responsibility(self) -> bool:
        """Return false unless a link is explicitly marked as verified by source."""
        return any(
            link.confidence is ResolutionConfidence.MATCHED_RECORD
            and not link.verification_required
            for link in self.links
        )

    def require_source(self) -> None:
        """Fail closed if the result contains no traceable source references."""
        if not self.links or not any(link.source_refs for link in self.links):
            raise ValueError("Responsibility resolution requires traceable source references")


class ResponsibilityResolver(Protocol):
    """Provider-neutral boundary for resolving responsibility candidates."""

    def resolve(
        self, observation: ResponsibilityObservation
    ) -> ResponsibilityResolution:
        ...
