"""Provider-neutral civic-document drafting capability.

The adapter orchestrates document drafting and delegates language translation
to the language service. It does not own channel/runtime behavior or legal
authority.
"""
from __future__ import annotations

import json
from typing import Any, Dict

import requests

from src.core.municipal_profiles import fetch_profile_by_code
from src.core.settings import ai_settings
from src.services.language_service import LanguageService


class JanavaniLegalAgent:
    """Optional AI adapter for structured civic-document drafting."""

    system_prompt = (
        "You only function as a civic-document drafting assistant. Do not answer "
        "questions outside civic-document drafting or engage in unrelated chat. "
        "Return valid JSON only. Do not provide legal "
        "advice or assert legal conclusions. Never invent authorities, laws, evidence, "
        "official actions, acknowledgements, or verification states. Mark claims that "
        "require source verification and human review."
    )

    def __init__(self, http_session: requests.Session | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)
        self._language_service = LanguageService(
            http_session=self._session,
            timeout=self._timeout,
        )

    def translate_input_if_needed(self, text: str, target_lang: str = "en") -> str:
        """Translate citizen input when configured; retain source text on failure."""
        return self._language_service.translate_input_if_needed(text, target_lang)

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
        self, citizen_issue: str, location_code: str | None = None
    ) -> Dict[str, Any]:
        """Draft a structured civic document with optional local administrative context."""
        issue = citizen_issue.strip()
        if not issue:
            return {
                "status": "invalid_input",
                "ai_used": False,
                "message": "A citizen issue is required.",
            }

        if not ai_settings.OPENROUTER_API_KEY or not ai_settings.LEGAL_DRAFTING_MODEL:
            return self._fallback(issue)

        regional_profile = (
            fetch_profile_by_code(location_code) if location_code else {}
        )
        prompt = self.system_prompt
        if regional_profile:
            prompt += (
                "\nUse the following local administrative profile as context only; "
                "do not infer or fabricate facts beyond it: "
                + json.dumps(regional_profile, ensure_ascii=False)
            )

        endpoint = ai_settings.OPENROUTER_URL.rstrip("/")
        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": ai_settings.LEGAL_DRAFTING_MODEL,
            "messages": [
                {"role": "system", "content": prompt},
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
                "result": body,
            }
        except (requests.RequestException, ValueError):
            return self._fallback(issue)
