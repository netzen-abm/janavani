"""Canonical FastAPI assembly boundary for Janavani."""

from fastapi import FastAPI

from src.platform.capabilities import registry
from src.web.feedback_router import router as feedback_router
from src.web.legislative_router import router as legislative_router
from src.web.constitutional_router import router as constitutional_router
from src.web.land_router import router as land_router
from src.web.case_router import router as case_router
from src.web.civic_action_router import router as civic_action_router


def create_canonical_app() -> FastAPI:
    app = FastAPI(title="Janavani Platform API", version="canonical-webapp")
    app.include_router(feedback_router)
    app.include_router(legislative_router)
    app.include_router(constitutional_router)
    app.include_router(land_router)
    app.include_router(case_router)
    app.include_router(civic_action_router)

    @app.get("/liveness", tags=["Platform"])
    async def liveness() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/version", tags=["Platform"])
    async def version() -> dict[str, str]:
        return {"service": "janavani-platform-api", "version": "canonical-webapp"}

    @app.get("/api/v1/capabilities", tags=["Platform"])
    async def capabilities() -> dict[str, object]:
        return {
            "items": [descriptor.__dict__ for descriptor in registry.list()],
            "health": registry.health(),
        }

    return app


app = create_canonical_app()
