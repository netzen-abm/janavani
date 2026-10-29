"""Independent public Dynamic Web presentation for JanaVani.

This is a distinct ASGI runtime from the authenticated WebApp and Telegram
webhook. Presentation, pathway selection and draft form UI have explicit
module boundaries; the canonical API owns identity, drafting policy and data.
"""
from __future__ import annotations

from fasthtml.common import Meta, Style, fast_app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.adapters.janavani_platform_client import client_for_request
from src.dynamic_web.pages import register_public_pages
from src.dynamic_web.pathways import register_pathway_routes
from src.dynamic_web.styles import DYNAMIC_WEB_STYLES
from src.ui.brand_assets import register_brand_assets
from src.ui.civic_drafting import register_civic_drafting_routes


app, rt = fast_app(
    hdrs=(
        Style(DYNAMIC_WEB_STYLES),
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
register_brand_assets(app)
register_civic_drafting_routes(rt, client_factory=client_for_request)


async def protect_responses(request, call_next):
    """Keep citizen-entered POST payloads and outputs out of shared caches."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.method in {"POST", "PUT", "PATCH"}:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=protect_responses)
