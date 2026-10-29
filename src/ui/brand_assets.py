# SPDX-License-Identifier: GPL-3.0-only
"""Shared immutable brand and illustration assets for JanaVani web surfaces."""
from __future__ import annotations

import os
from pathlib import Path

from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

_ASSET_ROOT = Path(__file__).resolve().parent / "assets"
_BRAND_MARK = _ASSET_ROOT / "brand" / "janavani-mark.svg"
_PREAMBLE_IMAGE = _ASSET_ROOT / "illustrations" / "preamble-of-india.webp"
_PATHWAY_IMAGE = _ASSET_ROOT / "illustrations" / "civic-action-pathway.webp"


def register_brand_assets(rt) -> None:
    """Register extensionless static routes to avoid FastHTML's extension route."""

    @rt("/brand-assets/brand/janavani-mark")
    def get_janavani_mark():
        return FileResponse(
            _BRAND_MARK,
            media_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @rt("/brand-assets/illustrations/preamble-of-india")
    def get_constitution_preamble_image():
        return FileResponse(
            _PREAMBLE_IMAGE,
            media_type="image/webp",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @rt("/brand-assets/illustrations/civic-action-pathway")
    def get_civic_action_pathway_image():
        return FileResponse(
            _PATHWAY_IMAGE,
            media_type="image/webp",
            headers={"Cache-Control": "public, max-age=86400"},
        )
