"""Hugging Face translation adapter behind the canonical AI provider contract.

The adapter performs provider I/O only. Authorization, consent, purpose and data
scope remain owned by the shared AI execution boundary.
"""
from __future__ import annotations

from typing import Any
import requests

from src.ai.provider import AIRequest, AIResponse
from src.core.settings import ai_settings


class HuggingFaceTranslationProvider:
    provider_id = "huggingface-translation"

    def __init__(self, http_session: requests.Session | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)

    def generate(self, request: AIRequest) -> AIResponse:
        token = ai_settings.HF_TOKEN
        model = request.model
        if not token or not model:
            raise ValueError("Hugging Face translation provider is not configured")
        text = request.messages[-1].get("content", "")
        endpoint = f"https://api-inference.huggingface.co/models/{model}"
        response = self._session.post(
            endpoint,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"inputs": text},
            timeout=self._timeout,
        )
        if getattr(response, "status_code", 200) >= 400:
            raise requests.HTTPError(f"Hugging Face translation request failed: {response.status_code}")
        body: Any = response.json()
        translated = None
        if isinstance(body, list) and body and isinstance(body[0], dict):
            translated = body[0].get("translation_text") or body[0].get("generated_text")
        elif isinstance(body, dict):
            translated = body.get("translation_text") or body.get("generated_text")
        if not translated:
            raise ValueError("Hugging Face returned no translation")
        return AIResponse(
            provider_id=self.provider_id,
            model=model,
            payload={"translated_text": translated},
        )
