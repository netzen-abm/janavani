"""Provider-neutral obligation resolution contracts.

Obligation resolution identifies potentially applicable public duties from
traceable sources. It does not assert breach, liability, misconduct, or guilt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ObligationConfidence(str, Enum):
    """Confidence levels for source-backed obligation matches."""

    OBSERVED = "observed"
    HIGH_CONFIDENCE = "high_confidence"
    MATCHED_RECORD = "matched_record"
    PROBABLE = "probable"
    VERIFICATION_REQUIRED = "verification_required"


class ObligationBasis(str, Enum):
    """Source basis supporting an obligation candidate."""

    OFFICIAL_RECORD = "official_record"
    SERVICE_STANDARD = "service_standard"
    POLICY = "policy"
    LAW = "law"
    REGULATION = "regulation"
    CONTRACT = "contract"
    WARRANTY = "warranty"
    USER_PROVIDED = "user_provided"


@dataclass(frozen=True)
class ObligationObservation:
    """Context used to identify potentially applicable obligations."""

    observation_id: str
    authority_id: str
    description: str
    asset_ref: str | None = None
    jurisdiction: dict[str, str] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("Observation id is required")
        if not self.authority_id.strip():
            raise ValueError("Authority id is required")
        if not self.description.strip():
            raise ValueError("Observation description is required")


@dataclass(frozen=True)
class ObligationLink:
    """A traceable candidate obligation; never a finding of breach."""

    obligation_id: str
    title: str
    description: str
    confidence: ObligationConfidence
    basis: ObligationBasis
    source_refs: tuple[str, ...] = field(default_factory=tuple)
    authority_id: str | None = None
    applicability: str | None = None
    remedy: str | None = None
    verification_required: bool = True
    notes: str | None = None


@dataclass(frozen=True)
class ObligationResolution:
    """Immutable obligation candidates with explicit provenance."""

    resolution_id: str
    observation_id: str
    links: tuple[ObligationLink, ...] = field(default_factory=tuple)
    resolved_at: str | None = None

    @property
    def has_verified_obligation(self) -> bool:
        """Return true only for an explicitly verified source-backed match."""
        return any(
            link.confidence is ObligationConfidence.MATCHED_RECORD
            and not link.verification_required
            for link in self.links
        )

    def require_source(self) -> None:
        """Fail closed when obligation candidates lack traceable sources."""
        if not self.links or not all(link.source_refs for link in self.links):
            raise ValueError("Obligation resolution requires traceable source references")


class ObligationResolver(Protocol):
    """Provider-neutral boundary for resolving applicable obligations."""

    def resolve(
        self, observation: ObligationObservation
    ) -> ObligationResolution:
        ...
