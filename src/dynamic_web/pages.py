"""Public route convergence for JanaVani's WordPress-owned portal."""
from __future__ import annotations

import os
from urllib.parse import urlsplit

from fastapi import HTTPException
from starlette.responses import RedirectResponse


def _redirect_to_wordpress_portal(path: str) -> RedirectResponse:
    """Return public informational navigation to the canonical WordPress origin."""
    base_url = os.getenv("JANAVANI_WORDPRESS_PORTAL_URL", "").strip().rstrip("/")
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise HTTPException(
            status_code=503,
            detail="The canonical JanaVani WordPress portal is not configured.",
        )
    return RedirectResponse(
        f"{base_url}{path}",
        status_code=307,
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
        },
    )


def register_public_pages(rt) -> None:
    """Redirect public portal paths instead of maintaining duplicate public content."""

    @rt("/")
    def get_home():
        """Keep WordPress as the only public landing page."""
        return _redirect_to_wordpress_portal("/")

    @rt("/privacy")
    def get_privacy():
        """Keep the authoritative privacy and safety explanation in WordPress."""
        return _redirect_to_wordpress_portal("/privacy-safety/")
