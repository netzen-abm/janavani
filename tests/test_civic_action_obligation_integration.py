from src.capabilities.obligation import ObligationResolutionRequest
from src.core.obligation import ObligationObservation


def test_vertical_slice_exposes_obligation_resolution_with_injected_records():
    from tests.helpers import build_vertical_slice

    slice_ = build_vertical_slice(
        obligation_records={
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
    from src.storage.repositories.obligation import AuthorityBackedObligationResolver

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
