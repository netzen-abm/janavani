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

from src.core.settings import ai_settings


class JanavaniLegalAgent:
    """Optional AI adapter for structured civic-document drafting."""

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

    def draft_legal_document(self, citizen_issue: str) -> Dict[str, Any]:
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

        if not ai_settings.OPENROUTER_API_KEY or not ai_settings.LEGAL_DRAFTING_MODEL:
            return self._fallback(issue)

        endpoint = ai_settings.OPENROUTER_URL.rstrip("/")
        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": ai_settings.LEGAL_DRAFTING_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Create a structured civic-document draft from the user's facts. "
                        "Do not invent authorities, laws, evidence, official actions, "
                        "acknowledgements, or verification states. Clearly mark claims "
                        "that require source verification and human review."
                    ),
                },
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
