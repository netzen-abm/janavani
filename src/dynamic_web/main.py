"""Independent public Dynamic Web presentation for JanaVani.

This is a distinct ASGI runtime from the authenticated WebApp and Telegram
webhook. Presentation, pathway selection and draft form UI have explicit
module boundaries; the canonical API owns identity, drafting policy and data.
"""
from __future__ import annotations

import os
from urllib.parse import urlencode, urlsplit

from fastapi import HTTPException
from fasthtml.common import Link, Meta, Style, fast_app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from src.adapters.janavani_platform_client import client_for_request
from src.dynamic_web.pages import register_public_pages
from src.dynamic_web.pathways import register_pathway_routes
from src.dynamic_web.styles import DYNAMIC_WEB_STYLES
from src.ui.brand_assets import register_brand_assets


app, rt = fast_app(
    hdrs=(
        Style(DYNAMIC_WEB_STYLES),
        Link(rel="icon", type="image/svg+xml", href="/favicon.svg"),
        Meta(
            name="description",
            content=(
                "JanaVani helps citizens choose civic pathways and prepare editable "
                "documents through reusable templates, with optional consent-gated AI improvement."
            ),
        ),
        Meta(name="theme-color", content="#071d30"),
    )
)


@rt("/liveness")
def get_liveness():
    """Surface health check; does not require the API or messaging service."""
    return JSONResponse({"status": "alive", "surface": "dynamic-web"})


register_public_pages(rt)
register_pathway_routes(app)
register_brand_assets(rt)

def _redirect_to_canonical_webapp(
    request: Request, allowed_query_keys: frozenset[str]
) -> RedirectResponse:
    """Keep drafting and owner-scoped saved formats on the authenticated WebApp origin."""
    base_url = os.getenv("JANAVANI_CANONICAL_WEBAPP_URL", "").strip().rstrip("/")
    parsed = urlsplit(base_url)
    local_http = parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        not parsed.netloc
        or (parsed.scheme != "https" and not local_http)
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise HTTPException(
            status_code=503,
            detail="The canonical Janavani WebApp destination is not configured.",
        )
    query = urlencode([
        (key, value)
        for key, value in request.query_params.multi_items()
        if key in allowed_query_keys and len(value) <= 120
    ])
    target = f"{base_url}{request.url.path}"
    if query:
        target = f"{target}?{query}"
    return RedirectResponse(
        target,
        status_code=307,
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
        },
    )


@rt("/ai-drafting")
def redirect_civic_drafting(request: Request):
    """Route every public draft entry point to the canonical WebApp."""
    return _redirect_to_canonical_webapp(
        request, frozenset({"template_id", "format_id"})
    )


@rt("/citizen-formats")
def redirect_citizen_formats(request: Request):
    """Keep private citizen formats on the authenticated WebApp origin."""
    return _redirect_to_canonical_webapp(request, frozenset())


@rt("/citizen-formats/confirm")
def redirect_citizen_format_confirmation(request: Request):
    """Carry only canonical template IDs into private-format confirmation."""
    return _redirect_to_canonical_webapp(
        request, frozenset({"template_id", "template_version"})
    )


async def protect_responses(request, call_next):
    """Keep citizen-entered POST payloads and outputs out of shared caches."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    private_format_page = request.url.path.startswith("/citizen-formats") or (request.url.path == "/ai-drafting" and "format_id" in request.query_params)
    if request.method in {"POST", "PUT", "PATCH"} or private_format_page:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=protect_responses)