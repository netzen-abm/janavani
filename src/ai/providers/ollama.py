"""Ollama local provider adapter for the canonical AI provider contract.

Ollama is an execution provider only. Authorization, consent, purpose, data scope
and capability ownership remain outside this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import httpx

from src.ai.provider import AIRequest, AIResponse


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str = os.getenv("JANAVANI_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model: str = os.getenv("JANAVANI_OLLAMA_MODEL", "")
    timeout_seconds: float = float(os.getenv("JANAVANI_OLLAMA_TIMEOUT_SECONDS", "60"))


class OllamaProvider:
    """Canonical synchronous AIProvider adapter for a local Ollama server."""

    provider_id = "ollama-local"

    def __init__(self, settings: OllamaSettings | None = None, client: httpx.Client | None = None) -> None:
        self.settings = settings or OllamaSettings()
        self._client = client or httpx.Client(timeout=self.settings.timeout_seconds)

    def generate(self, request: AIRequest) -> AIResponse:
        selected_model = request.model or self.settings.model
        if not selected_model:
            raise ValueError("JANAVANI_OLLAMA_MODEL must be configured for Ollama generation")
        response = self._client.post(
            f"{self.settings.base_url.rstrip('/')}/api/chat",
            json={
                "model": selected_model,
                "messages": [dict(message) for message in request.messages],
                "stream": False,
            },
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        return AIResponse(
            provider_id=self.provider_id,
            model=selected_model,
            payload=body,
        )
