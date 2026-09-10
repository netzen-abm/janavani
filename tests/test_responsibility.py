"""Tests for the provider-neutral responsibility capability."""

import pytest

from src.capabilities.responsibility import (
    ResponsibilityCapability,
    ResponsibilityResolutionRequest,
)
from src.core.responsibility import (
    ResolutionConfidence,
    ResolutionBasis,
    ResponsibilityLink,
    ResponsibilityObservation,
    ResponsibilityResolution,
)


class Resolver:
    def __init__(self, resolution: ResponsibilityResolution) -> None:
        self.resolution = resolution

    def resolve(self, observation: ResponsibilityObservation) -> ResponsibilityResolution:
        return self.resolution


def observation() -> ResponsibilityObservation:
    return ResponsibilityObservation(
        observation_id="obs-1",
        description="Road surface defect observed",
        location={"city": "Bengaluru"},
        evidence_refs=("evidence-1",),
    )


def resolution(*, source_refs=("official-record-1",)) -> ResponsibilityResolution:
    return ResponsibilityResolution(
        resolution_id="resolution-1",
        observation_id="obs-1",
        links=(
            ResponsibilityLink(
                entity_type="contract",
                entity_id="contract-1",
                entity_name="Public Works Contract",
                confidence=ResolutionConfidence.MATCHED_RECORD,
                basis=ResolutionBasis.OFFICIAL_RECORD,
                source_refs=source_refs,
                verification_required=False,
            ),
        ),
    )


def test_responsibility_capability_requires_traceable_source() -> None:
    capability = ResponsibilityCapability(Resolver(resolution(source_refs=())))
    with pytest.raises(ValueError, match="traceable source"):
        capability.resolve(ResponsibilityResolutionRequest(observation()))


def test_responsibility_capability_returns_source_backed_candidates() -> None:
    result = ResponsibilityCapability(Resolver(resolution())).resolve(
        ResponsibilityResolutionRequest(observation())
    )
    assert result.links[0].entity_type == "contract"
    assert result.has_verified_responsibility is True


def test_responsibility_resolution_does_not_promote_probable_match_to_verified() -> None:
    candidate = ResponsibilityResolution(
        resolution_id="resolution-2",
        observation_id="obs-1",
        links=(
            ResponsibilityLink(
                entity_type="contractor",
                entity_id="contractor-1",
                entity_name="Candidate Contractor",
                confidence=ResolutionConfidence.PROBABLE,
                basis=ResolutionBasis.CONTRACT,
                source_refs=("contract-1",),
                verification_required=True,
            ),
        ),
    )
    assert candidate.has_verified_responsibility is False


def test_responsibility_capability_rejects_blank_observation() -> None:
    capability = ResponsibilityCapability(Resolver(resolution()))
    with pytest.raises(ValueError, match="Observation id is required"):
        capability.resolve(
            ResponsibilityResolutionRequest(
                ResponsibilityObservation(observation_id="", description="Road defect")
            )
        )
