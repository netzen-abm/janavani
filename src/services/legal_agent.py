"""Provider-neutral legal-document AI capability adapter.

This module is intentionally a thin orchestration boundary. It must not own
legal authority, source-of-truth facts, or channel/runtime behavior.

AI and translation are optional capabilities. When unavailable, the adapter
returns a truthful deterministic fallback rather than pretending success.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from src.core.municipal_profiles import fetch_profile_by_code
from src.core.settings import ai_settings


class JanavaniLegalAgent:
    """Optional AI adapter for structured civic-document drafting."""

    system_prompt = (
        "You are a structured civic-document function, not an open chat assistant. "
        "Only transform supplied citizen facts into a structured civic-document draft. "
        "Do not answer questions, provide legal advice, invent laws, authorities, "
        "evidence, official actions, acknowledgements, or verification states. "
        "Return strict JSON only. Legal advice must not be presented as certified advice. "
        "Mark claims requiring source verification and human review."
    )

    def __init__(self, http_session: requests.Session | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)

    @staticmethod
    def _fallback(citizen_issue: str) -> Dict[str, Any]:
        """Return a truthful degraded result without pretending AI succeeded."""
        return {
            "status": "degraded",
            "ai_used": False,
            "draft": citizen_issue,
            "message": "AI drafting is unavailable; continue with deterministic/manual review.",
        }

    def translate_input_if_needed(self, text: str, target_lang: str = "en") -> str:
        """Optionally translate citizen input through the configured HF endpoint.

        Translation is deliberately isolated from legal drafting. If credentials,
        the endpoint, or the remote service are unavailable, the original text is
        returned unchanged so civic participation is not blocked.
        """
        if not text or not text.strip() or target_lang != "en":
            return text

        api_key = ai_settings.HUGGINGFACE_API_KEY
        model = ai_settings.IIT_MADRAS_TRANSLATION_MODEL
        if not api_key or not model:
            return text

        endpoint = f"https://api-inference.huggingface.co/models/{model}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {"inputs": text}

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )
            if response.status_code != 200:
                return text
            body = response.json()
            if isinstance(body, list) and body and isinstance(body[0], dict):
                translated = body[0].get("generated_text")
                if translated:
                    return translated
            if isinstance(body, dict) and body.get("generated_text"):
                return body["generated_text"]
        except (requests.RequestException, ValueError, TypeError):
            pass
        return text

    def draft_legal_document(
        self, citizen_issue: str, location_code: str | None = None
    ) -> Dict[str, Any]:
        """Draft a structured civic document when an AI provider is available.

        This method deliberately does not provide legal advice or assert legal
        conclusions. Source-grounded legal information must be supplied by the
        appropriate evidence/knowledge capability and reviewed by the user.
        """
        issue = citizen_issue.strip()
        if not issue:
            return {
                "status": "invalid_input",
                "ai_used": False,
                "message": "A citizen issue is required.",
            }

        regional_profile = fetch_profile_by_code(location_code or "")

        if not ai_settings.OPENROUTER_API_KEY or not ai_settings.LEGAL_DRAFTING_MODEL:
            return self._fallback(issue)

        endpoint = ai_settings.OPENROUTER_URL.rstrip("/")
        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        dynamic_prompt = (
            f"{self.system_prompt} Regional municipal profile: {regional_profile}."
        )
        payload = {
            "model": ai_settings.LEGAL_DRAFTING_MODEL,
            "messages": [
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": issue},
            ],
            "response_format": {"type": "json_object"},
        }

        try:
            response = self._session.post(
                f"{endpoint}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            body = response.json()
            return {
                "status": "available",
                "ai_used": True,
                "provider": "openrouter",
                "model": ai_settings.LEGAL_DRAFTING_MODEL,
                "regional_profile": regional_profile,
                "result": body,
            }
        except (requests.RequestException, ValueError):
            return self._fallback(issue)
