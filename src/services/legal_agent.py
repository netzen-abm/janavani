"""Compatibility facade for the shared, scope-gated civic-draft AI service."""
from __future__ import annotations

from typing import Any

import requests

from src.access.capability_scope import CapabilityDataScope
from src.capabilities.translation import TranslationCapability
from src.core.settings import ai_settings
from src.identity.context import IdentityContext
from src.services.civic_draft_executor import CivicDraftAIExecutor


class JanavaniLegalAgent:
    """Optional AI drafting adapter; identity and consent are caller-owned."""

    def __init__(
        self,
        http_session: requests.Session | None = None,
        provider=None,
    ) -> None:
        session = http_session or requests.Session()
        self._drafts = CivicDraftAIExecutor(session, provider)
        self._translation = TranslationCapability(session)

    @property
    def provider_id(self) -> str:
        """Expose the provider ID needed for an exact remote-processing grant."""
        return self._drafts.provider_id

    def remote_consent_scope(
        self, *, location_code: str | None = None
    ) -> CapabilityDataScope:
        """Build consent for the exact fields and provider the request will use."""
        return self._drafts.remote_consent_scope(location_code=location_code)

    def translate_input_if_needed(
        self,
        text: str,
        target_lang: str = "en",
        consent_scope: CapabilityDataScope | None = None,
        *,
        identity: IdentityContext | None = None,
    ) -> str:
        """Translate only for a supplied authorized identity and exact consent scope."""
        if not text or not text.strip() or target_lang != "en":
            return text
        if identity is None or not identity.principal.has_capability("civic:translation"):
            return text
        try:
            return self._translation.translate(
                text, identity=identity, consent_scope=consent_scope
            )
        except (requests.RequestException, ValueError, TypeError, PermissionError):
            return text

    def draft_legal_document(
        self,
        citizen_issue: str,
        location_code: str | None = None,
        consent_scope: CapabilityDataScope | None = None,
        *,
        identity: IdentityContext | None = None,
        document_type: str = "civic complaint",
    ) -> dict[str, Any]:
        """Draft structured civic wording, not legal advice or verified facts.

        Remote AI requires a verified identity, capability authorization and
        exact processing consent. Outputs need source verification and must be
        reviewed by the citizen.
        """
        issue = citizen_issue.strip()
        if not issue:
            return {
                "status": "invalid_input",
                "ai_used": False,
                "message": "A citizen issue is required.",
            }
        if not ai_settings.OPENROUTER_API_KEY or not ai_settings.LEGAL_DRAFTING_MODEL:
            return {
                "status": "degraded",
                "ai_used": False,
                "draft": issue,
                "message": "AI drafting is unavailable; continue with deterministic/manual review.",
            }
        if identity is None:
            return {
                "status": "identity_required",
                "ai_used": False,
                "message": "A verified user identity is required for remote AI drafting.",
            }
        if not identity.principal.has_capability("civic:ai-draft"):
            return {
                "status": "not_authorized",
                "ai_used": False,
                "message": "This identity is not authorized to use AI drafting.",
            }
        return self._drafts.draft(
            issue,
            identity=identity,
            document_type=document_type,
            consent_scope=consent_scope,
            location_code=location_code,
        )
