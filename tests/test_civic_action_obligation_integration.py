from src.capabilities.civic_action_vertical_slice import (
    CivicActionVerticalSlice,
    CivicActionVerticalSliceDependencies,
)
from src.capabilities.obligation import ObligationCapability, ObligationResolutionRequest
from src.core.obligation import ObligationObservation
from src.storage.repositories.obligation import AuthorityBackedObligationResolver


def _vertical_slice_with_obligation_resolver(resolver):
    dependencies = CivicActionVerticalSliceDependencies(
        case_capability=None,
        civic_action_capability=None,
        document_review_capability=None,
        submission_capability=None,
        responsibility_capability=None,
        obligation_capability=ObligationCapability(resolver),
        case_repository=None,
        document_review_repository=None,
    )
    return CivicActionVerticalSlice(dependencies)


def test_vertical_slice_exposes_obligation_resolution():
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


def test_obligation_resolution_does_not_imply_breach():
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
