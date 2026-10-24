"""Canonical FastAPI assembly boundary for Janavani.

Surface routers are adapters. Shared civic-case lifecycle semantics live in
``src.core.civic_case`` and are not owned by Web.
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

from src.config.runtime import validate_runtime_configuration
from src.web.constitutional_router import router as constitutional_router
from src.web.civic_case_router import router as civic_case_router
from src.web.feedback_router import router as feedback_router
from src.web.land_router import router as land_router
from src.web.sos_router import router as sos_router
from src.web.legislative_router import router as legislative_router
from src.web.identity_pairing_router import router as identity_pairing_router


def create_canonical_app() -> FastAPI:
    """Create the canonical FastAPI application."""
    validate_runtime_configuration()
    app = FastAPI(title="Janavani Platform API", version="canonical-m3")

    app.include_router(feedback_router)
    app.include_router(legislative_router)
    app.include_router(constitutional_router)
    app.include_router(land_router)
    app.include_router(sos_router)
    app.include_router(civic_case_router)
    app.include_router(identity_pairing_router)

    static_dir = Path(__file__).absolute().parent / "static"

    @app.get("/app", include_in_schema=False)
    async def citizen_workspace() -> FileResponse:
        """Serve the local-only citizen drafting workspace."""
        return FileResponse(
            static_dir / "citizen-workspace.html",
            media_type="text/html",
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": (
                    "default-src 'none'; style-src 'unsafe-inline'; script-src 'self'; "
                    "connect-src 'none'; img-src 'self' data:; base-uri 'none'; "
                    "form-action 'none'; frame-ancestors 'none'"
                ),
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "X-Frame-Options": "DENY",
                "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            },
        )

    @app.get("/app.js", include_in_schema=False)
    async def citizen_workspace_script() -> FileResponse:
        """Serve the self-contained workspace script without third-party assets."""
        return FileResponse(
            static_dir / "citizen-workspace.js",
            media_type="text/javascript",
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": "default-src 'none'",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
            },
        )

    @app.api_route("/", methods=["GET", "HEAD"], tags=["Platform"])
    async def root() -> dict[str, object]:
        """Return a truthful service landing response instead of a root 404."""
        return {
            "service": "janavani-platform-api",
            "version": "canonical-m3",
            "status": "available",
            "citizen_workspace": "/app",
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

    return app


app = create_canonical_app()
