"""Integration tests for obligation resolution in the civic-action slice."""

import pytest

from src.capabilities.civic_action_vertical_slice import (
    CivicActionVerticalSlice,
    CivicActionVerticalSliceDependencies,
)
from src.capabilities.external_channel import ExternalChannelCapability
from src.capabilities.obligation import ObligationCapability, ObligationResolutionRequest
from src.core.obligation import ObligationObservation
from src.storage.repositories.external_channel import InMemoryExternalChannelRepository
from src.storage.repositories.obligation import AuthorityBackedObligationResolver


def _vertical_slice_with_obligation_resolver(resolver: AuthorityBackedObligationResolver) -> CivicActionVerticalSlice:
    dependencies = CivicActionVerticalSliceDependencies(
        case_capability=None,  # type: ignore[arg-type]
        civic_action_capability=None,  # type: ignore[arg-type]
        evidence_capability=None,  # type: ignore[arg-type]
        document_review_capability=None,  # type: ignore[arg-type]
        submission_capability=None,  # type: ignore[arg-type]
        responsibility_capability=None,  # type: ignore[arg-type]
        obligation_capability=ObligationCapability(resolver),
        external_channel_capability=ExternalChannelCapability(InMemoryExternalChannelRepository()),
        case_repository=None,  # type: ignore[arg-type]
        document_review_repository=None,  # type: ignore[arg-type]
    )
    return CivicActionVerticalSlice(dependencies)


def test_vertical_slice_exposes_source_backed_obligation_resolution() -> None:
    slice_ = _vertical_slice_with_obligation_resolver(
        AuthorityBackedObligationResolver(
            {
                "authority-1": [
                    {
                        "obligation_id": "obl-1",
                        "title": "Maintain public road",
                        "description": "Maintain the road in accordance with the applicable public service standard.",
                        "source_refs": ("source:road-standard",),
                        "verified": True,
                    }
                ]
            }
        )
    )

    result = slice_.resolve_obligation(
        ObligationResolutionRequest(
            ObligationObservation(
                observation_id="obs-1",
                authority_id="authority-1",
                description="Road surface is damaged",
            )
        )
    )

    assert result.observation_id == "obs-1"
    assert result.links[0].obligation_id == "obl-1"
    assert result.links[0].authority_id == "authority-1"
    assert result.has_verified_obligation is True


def test_obligation_resolution_does_not_imply_breach() -> None:
    result = AuthorityBackedObligationResolver(
        {
            "authority-1": [
                {
                    "obligation_id": "obl-1",
                    "title": "Maintain public road",
                    "description": "Maintain the road.",
                    "source_refs": ("source:1",),
                    "verified": True,
                }
            ]
        }
    ).resolve(
        ObligationObservation(
            observation_id="obs-2",
            authority_id="authority-1",
            description="Road surface is damaged",
        )
    )

    assert result.links[0].notes
    assert "breach" in result.links[0].notes


def test_obligation_resolution_fails_closed_without_traceable_source() -> None:
    with pytest.raises(ValueError, match="traceable source"):
        _vertical_slice_with_obligation_resolver(
            AuthorityBackedObligationResolver(
                {
                    "authority-1": [
                        {
                            "obligation_id": "obl-1",
                            "title": "Unsupported obligation",
                            "description": "No traceable source is supplied.",
                            "source_refs": (),
                            "verified": True,
                        }
                    ]
                }
            )
        ).resolve_obligation(
            ObligationResolutionRequest(
                ObligationObservation(
                    observation_id="obs-3",
                    authority_id="authority-1",
                    description="Road surface is damaged",
                )
            )
        )
