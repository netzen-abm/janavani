"""Canonical FastAPI assembly boundary for Janavani.

This module is intentionally separate from the historical ``src.web.app``
module. It assembles existing domain routers without importing the legacy
Flask/concatenated application module.

M3-D migration rule: domain behavior remains in existing router/service
modules until each domain is independently migrated and verified.
"""

from fastapi import FastAPI

from src.web.feedback_router import router as feedback_router
from src.web.legislative_router import router as legislative_router
from src.web.constitutional_router import router as constitutional_router
from src.web.land_router import router as land_router
from src.web.case_workflow_router import router as case_workflow_router


def create_canonical_app() -> FastAPI:
    """Create the canonical FastAPI assembly without importing legacy app.py."""
    app = FastAPI(title="Janavani Platform API", version="canonical-m3")

    app.include_router(feedback_router)
    app.include_router(legislative_router)
    app.include_router(constitutional_router)
    app.include_router(land_router)
    app.include_router(case_workflow_router)

    @app.get("/liveness", tags=["Platform"])
    async def liveness() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/version", tags=["Platform"])
    async def version() -> dict[str, str]:
        return {"service": "janavani-platform-api", "version": "canonical-m3"}

    return app


app = create_canonical_app()
