"""Canonical FastAPI assembly boundary for Janavani.

Surface routers are adapters. Shared civic-case lifecycle semantics live in
``src.core.civic_case`` and are not owned by Web.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from src.config.runtime import validate_runtime_configuration
from src.web.constitutional_router import router as constitutional_router
from src.web.civic_case_router import router as civic_case_router
from src.web.feedback_router import router as feedback_router
from src.web.land_router import router as land_router
from src.web.sos_router import router as sos_router
from src.web.legislative_router import router as legislative_router


def create_canonical_app() -> FastAPI:
    """Create the canonical FastAPI application."""
    validate_runtime_configuration()
    app = FastAPI(
        title="Janavani Platform API",
        version="canonical-m3",
        docs_url=None,
        redoc_url=None,
    )

    app.include_router(feedback_router)
    app.include_router(legislative_router)
    app.include_router(constitutional_router)
    app.include_router(land_router)
    app.include_router(sos_router)
    app.include_router(civic_case_router)

    @app.api_route("/", methods=["GET", "HEAD"], tags=["Platform"])
    async def root() -> dict[str, object]:
        """Return a truthful service landing response instead of a root 404."""
        return {
            "service": "janavani-platform-api",
            "version": "canonical-m3",
            "status": "available",
            "health": "/liveness",
            "version_endpoint": "/version",
            "openapi": "/openapi.json",
            "docs": "/docs",
        }

    @app.get("/liveness", tags=["Platform"])
    async def liveness() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/version", tags=["Platform"])
    async def version() -> dict[str, str]:
        return {"service": "janavani-platform-api", "version": "canonical-m3"}

    @app.get("/docs", tags=["Platform"], include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        """Custom Swagger UI with Vercel Web Analytics."""
        html = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )
        # Inject Vercel Analytics script before closing body tag
        html_content = html.body.decode("utf-8")
        analytics_script = '<script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>'
        html_content = html_content.replace("</body>", f"{analytics_script}</body>")
        return HTMLResponse(content=html_content)

    @app.get("/redoc", tags=["Platform"], include_in_schema=False)
    async def custom_redoc_html() -> HTMLResponse:
        """Custom ReDoc with Vercel Web Analytics."""
        html = get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
        )
        # Inject Vercel Analytics script before closing body tag
        html_content = html.body.decode("utf-8")
        analytics_script = '<script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>'
        html_content = html_content.replace("</body>", f"{analytics_script}</body>")
        return HTMLResponse(content=html_content)

    return app


app = create_canonical_app()
