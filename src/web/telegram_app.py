"""Dedicated webhook-only Telegram application.

This service hosts the existing JanaVani Telegram handlers over HTTPS. It never
starts getUpdates/polling and deliberately stays separate from the canonical API
runtime's production persistence gates.
"""
from fastapi import FastAPI

from src.web.telegram_webhook import router, telegram_application_lifespan

app = FastAPI(
    title="JanaVani Telegram Webhook",
    version="1.0.0",
    lifespan=telegram_application_lifespan,
)
app.include_router(router)


@app.get("/livez", tags=["Platform"])
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/", tags=["Platform"])
async def root() -> dict[str, str]:
    return {
        "service": "janavani-telegram-webhook",
        "status": "available",
        "health": "/livez",
        "webhook": "/telegram/webhook",
    }
