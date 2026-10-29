"""Shared brand-asset delivery for independently deployed JanaVani web surfaces.

The visual asset is packaged with the application so the public web experiences
do not depend on the showcase website being available at request time.
"""
from __future__ import annotations

from pathlib import Path

from starlette.responses import FileResponse

_BRAND_MARK = Path(__file__).resolve().parent / "assets" / "brand" / "janavani-mark.svg"


def register_brand_assets(rt) -> None:
    """Register the same first-party mark route on a FastHTML runtime."""

    @rt("/assets/brand/janavani-mark.svg")
    def get_janavani_mark():
        return FileResponse(
            _BRAND_MARK,
            media_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400"},
        )
