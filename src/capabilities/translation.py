"""Shared translation capability.

Translation is independently reusable across Web, messaging, mobile and AI
workflows. Provider access is protected by the canonical AI execution gateway.
"""
from __future__ import annotations

import requests

from src.access.capability_scope import (
    CapabilityDataScope,
    CapabilityDataScopePolicy,
    DataClassification,
    DataRequirement,
)
from src.access.scoped_execution_policy import ScopedExecutionPolicy
from src.ai.gateway import AIExecutionGateway, AIExecutionRequest
from src.ai.provider import AIRequest
from src.ai.providers.huggingface_translation import HuggingFaceTranslationProvider
from src.core.execution import CapabilityExecutionContext
from src.core.settings import ai_settings
from src.identity.context import IdentityContext
from src.identity.principal import Principal

CAPABILITY_ID = "civic:translation"
PURPOSE = "civic_translation"


class TranslationCapability:
    """Translate citizen text without owning provider or authorization policy."""

    def __init__(self, http_session: requests.Session | None = None) -> None:
        session = http_session or requests.Session()
        self._provider = HuggingFaceTranslationProvider(session)
        self._gateway = AIExecutionGateway(
            provider=self._provider,
            scoped_policy=ScopedExecutionPolicy(
                capability=CAPABILITY_ID,
                allowed_fields=frozenset({"citizen_text"}),
                allowed_providers=frozenset({self._provider.provider_id}),
                allowed_processing_modes=frozenset({"remote_model"}),
                allowed_purposes=frozenset({PURPOSE}),
            ),
            data_scope_policy=CapabilityDataScopePolicy(
                capability_id=CAPABILITY_ID,
                requirements=(
                    DataRequirement("citizen_text", DataClassification.PERSONAL),
                ),
            ),
        )

    def translate(
        self,
        text: str,
        *,
        identity: IdentityContext,
        consent_scope: CapabilityDataScope | None = None,
    ) -> str:
        if not text.strip():
            return text
        model = ai_settings.IIT_MADRAS_TRANSLATION_MODEL
        if not ai_settings.HF_TOKEN or not model:
            return text
        context = CapabilityExecutionContext.for_capability(
            identity,
            capability_id=CAPABILITY_ID,
            action="translate",
            surface="shared-capability",
        )
        result = self._gateway.generate(
            AIExecutionRequest(
                identity=identity,
                execution_context=context,
                request=AIRequest(
                    purpose=PURPOSE,
                    messages=({"role": "user", "content": text},),
                    model=model,
                    data_scope=("citizen_text",),
                ),
                provider=self._provider.provider_id,
                processing_mode="remote_model",
            ),
            consent_scope=consent_scope,
        )
        return str(result.payload["translated_text"])
