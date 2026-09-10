from src.capabilities.responsibility import (
    ResponsibilityCapability,
    ResponsibilityResolutionRequest,
)
from src.core.responsibility import (
    ResolutionBasis,
    ResolutionConfidence,
    ResponsibilityLink,
    ResponsibilityObservation,
    ResponsibilityResolution,
)
from src.storage.repositories.responsibility import InMemoryResponsibilityResolver


def _observation() -> ResponsibilityObservation:
    return ResponsibilityObservation(
        observation_id="obs-1",
        description="Road defect observed",
        location={"city": "Bengaluru"},
        evidence_refs=("evidence-1",),
    )


def test_resolution_requires_traceable_source() -> None:
    resolution = ResponsibilityResolution(
        resolution_id="res-1",
        observation_id="obs-1",
        links=(
            ResponsibilityLink(
                entity_type="contract",
                entity_id="contract-1",
                entity_name="Example Contract",
                confidence=ResolutionConfidence.PROBABLE,
                basis=ResolutionBasis.CONTRACT,
            ),
        ),
    )
    resolver = InMemoryResponsibilityResolver([resolution])

    try:
        ResponsibilityCapability(resolver).resolve(
            ResponsibilityResolutionRequest(_observation())
        )
    except ValueError as exc:
        assert "traceable source" in str(exc)
    else:
        raise AssertionError("Untraceable responsibility resolution must fail closed")


def test_resolution_preserves_source_and_does_not_promote_inference() -> None:
    resolution = ResponsibilityResolution(
        resolution_id="res-2",
        observation_id="obs-1",
        links=(
            ResponsibilityLink(
                entity_type="contractor",
                entity_id="contractor-1",
                entity_name="Example Contractor",
                confidence=ResolutionConfidence.PROBABLE,
                basis=ResolutionBasis.CONTRACT,
                source_refs=("official-record-1",),
                verification_required=True,
            ),
        ),
    )
    resolver = InMemoryResponsibilityResolver([resolution])

    result = ResponsibilityCapability(resolver).resolve(
        ResponsibilityResolutionRequest(_observation())
    )

    assert result.links[0].source_refs == ("official-record-1",)
    assert result.links[0].verification_required is True
    assert result.has_verified_responsibility is False
