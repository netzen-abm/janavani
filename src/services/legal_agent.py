"""Provider-neutral legal-document AI capability adapter.

This module is intentionally a thin orchestration boundary. It must not own
legal authority, source-of-truth facts, or channel/runtime behavior.

The active implementation provides a deterministic degraded path when AI
providers are unavailable. Provider/model selection remains configuration-
driven so future providers or local models can be introduced without
rewriting the capability contract.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from src.core.municipal_profiles import fetch_profile_by_code
from src.core.settings import ai_settings


class JanavaniLegalAgent:
    """Optional AI adapter for structured civic-document drafting."""

    SYSTEM_PROMPT = (
        "You are a bounded civic-document drafting assistant. "
        "Only assist with the requested civic-document task; do not provide open chat. "
        "Do not answer questions outside the requested civic-document task. "
        "Do not provide legal advice or invent authorities, laws, evidence, official "
        "actions, acknowledgements, addresses, or verification states. Return structured "
        "JSON and clearly mark claims requiring source verification and human review."
    )

    def __init__(self, http_session: requests.Session | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)
        self.system_prompt = self.SYSTEM_PROMPT

    @staticmethod
    def _fallback(citizen_issue: str) -> Dict[str, Any]:
        """Return a truthful degraded result without pretending AI succeeded."""
        return {
            "status": "degraded",
            "ai_used": False,
            "draft": citizen_issue,
            "message": "AI drafting is unavailable; continue with deterministic/manual review.",
        }

    def draft_legal_document(
        self,
        citizen_issue: str,
        location_code: str | None = None,
    ) -> Dict[str, Any]:
        """Draft a structured civic document when an AI provider is available."""
        issue = citizen_issue.strip()
        if not issue:
            return {
                "status": "invalid_input",
                "ai_used": False,
                "message": "A citizen issue is required.",
            }

        regional_profile = None
        if location_code:
            regional_profile = fetch_profile_by_code(location_code)

        if not ai_settings.OPENROUTER_API_KEY or not ai_settings.LEGAL_DRAFTING_MODEL:
            return self._fallback(issue)

        endpoint = ai_settings.OPENROUTER_URL.rstrip("/")
        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        user_payload: dict[str, Any] = {"issue": issue}
        if regional_profile:
            user_payload["regional_profile"] = regional_profile

        payload = {
            "model": ai_settings.LEGAL_DRAFTING_MODEL,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": str(user_payload)},
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
                "result": body,
            }
        except (requests.RequestException, ValueError):
            return self._fallback(issue)

    def translate_input_if_needed(self, text: str, target_lang: str = "en") -> str:
        """Translate input through the configured service when enabled."""
        if not text:
            return text
        if target_lang.lower() in {"", "auto"}:
            return text
        token = getattr(ai_settings, "HUGGINGFACE_API_KEY", None)
        endpoint = getattr(ai_settings, "HUGGINGFACE_TRANSLATION_URL", None)
        if not token or not endpoint:
            return text

        try:
            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
                json={"inputs": text, "parameters": {"target_lang": target_lang}},
                timeout=self._timeout,
            )
            response.raise_for_status()
            body = response.json()
            if isinstance(body, list) and body and isinstance(body[0], dict):
                translated = body[0].get("translation_text") or body[0].get("generated_text")
                return str(translated) if translated else text
            if isinstance(body, dict):
                translated = body.get("translation_text") or body.get("generated_text")
                return str(translated) if translated else text
        except (requests.RequestException, ValueError, TypeError):
            pass
        return text
