"""Provider-neutral legal-document AI capability adapter.

This module is intentionally a thin orchestration boundary. It must not own
legal authority, source-of-truth facts, or channel/runtime behavior.

AI and translation are optional capabilities. When unavailable, the adapter
returns a truthful deterministic fallback rather than pretending success.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy, DataClassification, DataRequirement
from src.access.scoped_execution_policy import ScopedExecutionPolicy
from src.ai.gateway import AIExecutionGateway, AIExecutionRequest
from src.ai.provider import AIRequest, AIProvider
from src.capabilities.translation import TranslationCapability
from src.ai.composition import create_openrouter_provider
from src.core.municipal_profiles import fetch_profile_by_code
from src.core.settings import ai_settings
from src.identity.context import IdentityContext
from src.services.civic_draft_schema import InvalidAIDraftOutput, normalize_provider_draft


class JanavaniLegalAgent:
    """Optional AI adapter for structured civic-document drafting."""

    system_prompt = (
        "You are a structured civic-document function, not an open chat assistant. "
        "Only transform supplied citizen facts into a structured civic-document draft. "
        "Do not answer questions, provide legal advice, invent laws, authorities, "
        "evidence, official actions, acknowledgements, or verification states. "
        "Return strict JSON only, with subject, proposal_or_notice, "
        "part_i_interrogatories, requested_conditions, and remedies_reserved fields. "
        "Never invent statutes, legal citations, sources, deadlines, people, facts, "
        "verified authorities, or evidence. Do not output legal_framework or references. "
        "Keep every suggested request clearly editable and subject to citizen review."
    )

    def __init__(self, http_session: requests.Session | None = None, provider: AIProvider | None = None) -> None:
        self._session = http_session or requests.Session()
        self._timeout = (3, 15)
        self._provider = provider or create_openrouter_provider(self._session)
        self._translation = TranslationCapability(self._session)
        self._ai_gateway = AIExecutionGateway(
            provider=self._provider,
            scoped_policy=ScopedExecutionPolicy(
                capability="civic:ai-draft",
                allowed_fields=frozenset({"citizen_issue", "regional_routing_metadata"}),
                allowed_providers=frozenset({self._provider.provider_id}),
                allowed_processing_modes=frozenset({"remote_model"}),
                allowed_purposes=frozenset({"civic_document_drafting"}),
            ),
            data_scope_policy=CapabilityDataScopePolicy(
                capability_id="civic:ai-draft",
                requirements=(
                    DataRequirement("citizen_issue", DataClassification.PERSONAL),
                    DataRequirement("regional_routing_metadata", DataClassification.NON_SENSITIVE),
                ),
            ),
        )

    @staticmethod
    @property
    def provider_id(self) -> str:
        """Identify the configured adapter for an exact consent grant."""
        return self._provider.provider_id

    def remote_consent_scope(self, *, location_code: str | None = None) -> CapabilityDataScope:
        """Build a consent scope for only the fields sent to the remote provider."""
        fields = {"citizen_issue"}
        if location_code:
            fields.add("regional_routing_metadata")
        return CapabilityDataScope(
            capability_id="civic:ai-draft",
            purpose="civic_document_drafting",
            approved_fields=frozenset(fields),
            provider=self.provider_id,
            processing_mode="remote_model",
        )

    @staticmethod
    def _fallback(citizen_issue: str) -> Dict[str, Any]:
        """Return a truthful degraded result without pretending AI succeeded."""
        return {
            "status": "degraded",
            "ai_used": False,
            "draft": citizen_issue,
            "message": "AI drafting is unavailable; continue with deterministic/manual review.",
        }

    def translate_input_if_needed(self, text: str, target_lang: str = "en", consent_scope: CapabilityDataScope | None = None) -> str:
        """Compatibility wrapper over the shared Translation capability."""
        if not text or not text.strip() or target_lang != "en":
            return text
        try:
            from src.identity.context import IdentityContext
            from src.identity.principal import Principal

            identity = IdentityContext(
                principal=Principal(
                    principal_id="translation-service",
                    capabilities=frozenset({"civic:translation"}),
                )
            )
            return self._translation.translate(text, identity=identity, consent_scope=consent_scope)
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

        data_scope = ("citizen_issue", "regional_routing_metadata") if location_code else ("citizen_issue",)
        request = AIRequest(
            purpose="civic_document_drafting",
            messages=(
                {
                    "role": "system",
                    "content": (
                        f"{self.system_prompt} Document type: {document_type}. "
                        "Do not make legal conclusions. If the input is an existing draft, "
                        "preserve its purpose and factual claims while improving clarity. "
                        + (
                            f"Regional municipal profile: {regional_profile}. Treat it as "
                            "contextual routing metadata, not verified legal authority."
                            if location_code else ""
                        )
                    ),
                },
                {"role": "user", "content": issue},
            ),
            model=ai_settings.LEGAL_DRAFTING_MODEL,
            data_scope=data_scope,
        )

        try:
            from src.core.execution import CapabilityExecutionContext

            execution_identity = identity
            execution_context = CapabilityExecutionContext.for_capability(
                execution_identity,
                capability_id="civic:ai-draft",
                action="draft",
                surface=identity.principal.interface or "shared-capability",
            )
            generated = self._ai_gateway.generate(
                AIExecutionRequest(
                    identity=execution_identity,
                    execution_context=execution_context,
                    request=request,
                    provider=self._provider.provider_id,
                    processing_mode="remote_model",
                ),
                consent_scope=consent_scope,
            )
            try:
                structured = normalize_provider_draft(
                    dict(generated.payload), fallback_subject=issue.splitlines()[0][:200]
                )
            except InvalidAIDraftOutput:
                return {
                    "status": "degraded",
                    "ai_used": True,
                    "provider": generated.provider_id,
                    "model": generated.model,
                    "draft": issue,
                    "message": "AI output could not be validated; no generated sections were applied.",
                }
            return {
                "status": "available",
                "ai_used": True,
                "provider": generated.provider_id,
                "model": generated.model,
                "regional_profile": regional_profile if location_code else None,
                "structured_draft": structured,
            }
        except PermissionError as exc:
            return {
                "status": "consent_required",
                "ai_used": False,
                "message": str(exc),
            }
        except (requests.RequestException, ValueError, TypeError):
            return self._fallback(issue)
