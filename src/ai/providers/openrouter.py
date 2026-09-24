"""OpenRouter implementation of the provider-neutral AI contract."""
from __future__ import annotations

from typing import Any, Mapping

import requests

from src.ai.provider import AIRequest, AIResponse
from src.core.settings import ai_settings


class OpenRouterProvider:
    provider_id = "openrouter"

    def __init__(self, http_session: requests.Session | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)

    def generate(self, request: AIRequest) -> AIResponse:
        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [dict(message) for message in request.messages],
            "response_format": {"type": "json_object"},
        }
        response = self._session.post(
            f"{ai_settings.OPENROUTER_URL.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        body = response.json()
        return AIResponse(provider_id=self.provider_id, model=request.model, payload=body)
