# SPDX-License-Identifier: GPL-3.0-only
"""Shared immutable brand and illustration assets for JanaVani web surfaces."""
from __future__ import annotations

import os
from pathlib import Path

from starlette.datastructures import Headers
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

_ASSET_ROOT = Path(__file__).resolve().parent / "assets"


class CachedBrandStaticFiles(StaticFiles):
    """Serve the packaged allow-listed asset directory with an explicit cache policy."""

    def file_response(
        self,
        full_path: str,
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = "public, max-age=86400"
        return response


def register_brand_assets(app) -> None:
    """Mount the shared SVG/WebP directory once on each independent web application."""
    app.mount(
        "/brand-assets",
        CachedBrandStaticFiles(directory=str(_ASSET_ROOT), check_dir=True),
        name="brand-assets",
    )
