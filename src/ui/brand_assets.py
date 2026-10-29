# SPDX-License-Identifier: GPL-3.0-only
"""Shared brand-asset delivery for independently deployed JanaVani web surfaces.

The visual asset is packaged with the application so the public web experiences
do not depend on the showcase website being available at request time.
"""
from __future__ import annotations

from pathlib import Path

from starlette.responses import FileResponse

_ASSET_ROOT = Path(__file__).resolve().parent / "assets"
_BRAND_MARK = _ASSET_ROOT / "brand" / "janavani-mark.svg"
_PREAMBLE_IMAGE = _ASSET_ROOT / "illustrations" / "preamble-of-india.webp"
_PATHWAY_IMAGE = _ASSET_ROOT / "illustrations" / "civic-action-pathway.webp"


def register_brand_assets(rt) -> None:
    """Register the same first-party mark route on a FastHTML runtime."""

    @rt("/brand-assets/brand/janavani-mark.svg")
    def get_janavani_mark():
        return FileResponse(
            _BRAND_MARK,
            media_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @rt("/brand-assets/illustrations/preamble-of-india.webp")
    def get_constitution_preamble_image():
        return FileResponse(
            _PREAMBLE_IMAGE,
            media_type="image/webp",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @rt("/brand-assets/illustrations/civic-action-pathway.webp")
    def get_civic_action_pathway_image():
        return FileResponse(
            _PATHWAY_IMAGE,
            media_type="image/webp",
            headers={"Cache-Control": "public, max-age=86400"},
        )
