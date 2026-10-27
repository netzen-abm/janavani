"""Provider adapter for optional citizen-input translation."""
from __future__ import annotations

from typing import Any

import requests

from src.core.settings import ai_settings


class LanguageService:
    """Translate citizen input through the configured Hugging Face model."""

    def __init__(
        self,
        http_session: requests.Session | None = None,
        timeout: tuple[int, int] = (3, 15),
    ) -> None:
        self._session = http_session or requests.Session()
        self._timeout = timeout

    def translate_input_if_needed(self, text: str, target_lang: str = "en") -> str:
        """Return translated text, falling back to the original on provider failure."""
        if not text or target_lang.lower() in {"", "auto", "source"}:
            return text

        api_key = ai_settings.HUGGINGFACE_API_KEY
        model = ai_settings.IIT_MADRAS_TRANSLATION_MODEL
        if not api_key or not model:
            return text

        endpoint = f"https://api-inference.huggingface.co/models/{model}"
        try:
            response = self._session.post(
                endpoint,
                headers={"Authorization": f"Bearer {api_key}"},
                json={"inputs": text, "parameters": {"target_lang": target_lang}},
                timeout=self._timeout,
            )
            if response.status_code != 200:
                return text
            payload: Any = response.json()
            if isinstance(payload, dict):
                translated = payload.get("generated_text")
                return translated.strip() if isinstance(translated, str) and translated.strip() else text
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                translated = payload[0].get("translation_text") or payload[0].get("generated_text")
                return translated.strip() if isinstance(translated, str) and translated.strip() else text
        except (requests.RequestException, ValueError):
            return text
        return text
