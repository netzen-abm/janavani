"""Canonical FastAPI assembly boundary for Janavani.

Surface routers are adapters. Shared civic-case lifecycle semantics live in
``src.core.civic_case`` and are not owned by Web.
"""

from fastapi import FastAPI

from src.web.constitutional_router import router as constitutional_router
from src.web.civic_case_router import router as civic_case_router
from src.web.feedback_router import router as feedback_router
from src.web.land_router import router as land_router
from src.web.legislative_router import router as legislative_router


def create_canonical_app() -> FastAPI:
    """Create the canonical FastAPI application."""
    app = FastAPI(title="Janavani Platform API", version="canonical-m3")

    app.include_router(feedback_router)
    app.include_router(legislative_router)
    app.include_router(constitutional_router)
    app.include_router(land_router)
    app.include_router(civic_case_router)

    @app.get("/liveness", tags=["Platform"])
    async def liveness() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/version", tags=["Platform"])
    async def version() -> dict[str, str]:
        return {"service": "janavani-platform-api", "version": "canonical-m3"}

    return app


app = create_canonical_app()
