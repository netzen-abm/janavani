"""Provider-neutral legal-document AI capability adapter.

This module is intentionally a thin orchestration boundary. It must not own
legal authority, source-of-truth facts, or channel/runtime behavior.

AI and translation are optional capabilities. When unavailable, the adapter
returns a truthful deterministic fallback rather than pretending success.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from src.ai.provider import AIRequest, AIProvider
from src.ai.providers.openrouter import OpenRouterProvider
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

    def __init__(self, http_session: requests.Session | None = None, provider: AIProvider | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)
        self._provider = provider or OpenRouterProvider(self._session)

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
        """Optionally translate citizen input via the configured Hugging Face model.

        Translation is isolated from legal drafting. Missing configuration or provider
        failure returns the original citizen text so civic participation is not blocked.
        """
        if not text or not text.strip() or target_lang != "en":
            return text

        token = ai_settings.HF_TOKEN
        model = ai_settings.IIT_MADRAS_TRANSLATION_MODEL
        if not token or not model:
            return text

        endpoint = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        try:
            response = self._session.post(
                endpoint,
                headers=headers,
                json={"inputs": text},
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

        request = AIRequest(
            purpose="civic_document_drafting",
            messages=(
                {
                    "role": "system",
                    "content": (
                        f"{self.system_prompt} Regional municipal profile: {regional_profile}. "
                        "Treat the profile as contextual routing metadata, not as independently "
                        "verified legal authority; claims still require source verification and review."
                    ),
                },
                {"role": "user", "content": issue},
            ),
            model=ai_settings.LEGAL_DRAFTING_MODEL,
            data_scope=("citizen_issue", "regional_routing_metadata"),
        )

        try:
            generated = self._provider.generate(request)
            return {
                "status": "available",
                "ai_used": True,
                "provider": generated.provider_id,
                "model": generated.model,
                "regional_profile": regional_profile,
                "result": generated.payload,
            }
        except (requests.RequestException, ValueError, TypeError):
            return self._fallback(issue)
