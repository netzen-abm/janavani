from __future__ import annotations

import pytest

from src.capabilities.obligation import ObligationCapability, ObligationResolutionRequest
from src.core.obligation import (
    ObligationBasis,
    ObligationObservation,
)
from src.storage.repositories.obligation import AuthorityBackedObligationResolver


def _observation() -> ObligationObservation:
    return ObligationObservation(
        observation_id="obs-1",
        authority_id="auth-1",
        description="Observed unresolved road defect",
        asset_ref="road-1",
        jurisdiction={"city": "Bengaluru"},
        evidence_refs=("ev-1",),
    )


def test_verified_source_backed_obligation_is_resolved() -> None:
    resolver = AuthorityBackedObligationResolver(
        {
            "auth-1": [
                {
                    "obligation_id": "obl-1",
                    "title": "Road maintenance duty",
                    "description": "Maintain the applicable public road service.",
                    "basis": ObligationBasis.SERVICE_STANDARD.value,
                    "source_refs": ("source-1",),
                    "verified": True,
                    "applicability": "Applicable public road service",
                    "remedy": "Repair or otherwise address the reported defect",
                }
            ]
        }
    )

    resolution = ObligationCapability(resolver).resolve(
        ObligationResolutionRequest(_observation())
    )

    assert resolution.has_verified_obligation is True
    assert resolution.links[0].source_refs == ("source-1",)
    assert resolution.links[0].verification_required is False


def test_unverified_obligation_remains_verification_required() -> None:
    resolver = AuthorityBackedObligationResolver(
        {
            "auth-1": [
                {
                    "obligation_id": "obl-2",
                    "title": "Potential service obligation",
                    "description": "A source-backed candidate requiring review.",
                    "source_refs": ("source-2",),
                    "verified": False,
                }
            ]
        }
    )

    resolution = ObligationCapability(resolver).resolve(
        ObligationResolutionRequest(_observation())
    )

    assert resolution.has_verified_obligation is False
    assert resolution.links[0].verification_required is True


def test_source_less_records_fail_closed() -> None:
    resolver = AuthorityBackedObligationResolver(
        {
            "auth-1": [
                {
                    "obligation_id": "obl-3",
                    "title": "Unsupported obligation",
                    "description": "No traceable source is supplied.",
                    "verified": True,
                }
            ]
        }
    )

    with pytest.raises(ValueError, match="traceable source"):
        ObligationCapability(resolver).resolve(
            ObligationResolutionRequest(_observation())
        )


def test_observation_requires_authority_and_description() -> None:
    with pytest.raises(ValueError, match="Authority id"):
        ObligationObservation(
            observation_id="obs-2",
            authority_id=" ",
            description="Observed issue",
        )

    with pytest.raises(ValueError, match="Observation description"):
        ObligationObservation(
            observation_id="obs-3",
            authority_id="auth-1",
            description=" ",
        )
