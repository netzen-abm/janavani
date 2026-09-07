"""Optional local Ollama AI provider adapter.

Ollama is intentionally treated as an AI provider, not as a Janavani domain
runtime. The adapter keeps local model execution behind the existing AI
provider boundary so citizens/developers can choose local inference without
coupling the product core to Ollama.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import httpx


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str = os.getenv("JANAVANI_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model: str = os.getenv("JANAVANI_OLLAMA_MODEL", "")
    timeout_seconds: float = float(os.getenv("JANAVANI_OLLAMA_TIMEOUT_SECONDS", "60"))


class OllamaProvider:
    """Minimal chat-generation adapter for an Ollama server."""

    provider_id = "ollama-local"

    def __init__(self, settings: OllamaSettings | None = None, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings or OllamaSettings()
        self._client = client or httpx.AsyncClient(timeout=self.settings.timeout_seconds)

    async def generate(self, messages: list[dict[str, str]], *, model: str | None = None) -> dict[str, Any]:
        selected_model = model or self.settings.model
        if not selected_model:
            raise ValueError("JANAVANI_OLLAMA_MODEL must be configured for Ollama generation")
        response = await self._client.post(
            f"{self.settings.base_url.rstrip('/')}/api/chat",
            json={"model": selected_model, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        return response.json()
