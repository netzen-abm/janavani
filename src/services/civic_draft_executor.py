"""Remote AI execution boundary for structured civic-draft assistance.

This service owns provider calls, identity/scope enforcement and validation of
untrusted model output. It never persists the citizen's input or generated draft.
"""
from __future__ import annotations

from typing import Any

import requests

from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy, DataClassification, DataRequirement
from src.access.scoped_execution_policy import ScopedExecutionPolicy
from src.ai.composition import create_openrouter_provider
from src.ai.gateway import AIExecutionGateway, AIExecutionRequest
from src.ai.provider import AIProvider, AIRequest
from src.core.execution import CapabilityExecutionContext
from src.core.municipal_profiles import fetch_profile_by_code
from src.core.settings import ai_settings
from src.identity.context import IdentityContext
from src.services.civic_draft_schema import InvalidAIDraftOutput, normalize_provider_draft

CAPABILITY_ID = "civic:ai-draft"
PURPOSE = "civic_document_drafting"

_SYSTEM_PROMPT = (
    "Transform the citizen's issue or existing draft into editable civic wording. "
    "Return strict JSON with subject, proposal_or_notice, part_i_interrogatories, "
    "requested_conditions and remedies_reserved. Preserve stated facts and intent. "
    "Never invent facts, statutes, citations, sources, deadlines, people, authorities, "
    "evidence, verification states or official actions. No legal advice/effect claims; "
    "citizen review is required."
)


class CivicDraftAIExecutor:
    """Execute optional remote AI drafting after identity and data-scope checks."""

    def __init__(
        self,
        http_session: requests.Session | None = None,
        provider: AIProvider | None = None,
    ) -> None:
        self._session = http_session or requests.Session()
        self._provider = provider or create_openrouter_provider(self._session)
        self._gateway = AIExecutionGateway(
            provider=self._provider,
            scoped_policy=ScopedExecutionPolicy(
                capability=CAPABILITY_ID,
                allowed_fields=frozenset({"citizen_issue", "regional_routing_metadata"}),
                allowed_providers=frozenset({self._provider.provider_id}),
                allowed_processing_modes=frozenset({"remote_model"}),
                allowed_purposes=frozenset({PURPOSE}),
            ),
            data_scope_policy=CapabilityDataScopePolicy(
                capability_id=CAPABILITY_ID,
                requirements=(
                    DataRequirement("citizen_issue", DataClassification.PERSONAL),
                    DataRequirement("regional_routing_metadata", DataClassification.NON_SENSITIVE),
                ),
            ),
        )

    @property
    def provider_id(self) -> str:
        return self._provider.provider_id

    def remote_consent_scope(
        self, *, location_code: str | None = None
    ) -> CapabilityDataScope:
        """Build an exact consent grant for the fields sent to the remote model."""
        fields = {"citizen_issue"}
        if location_code:
            fields.add("regional_routing_metadata")
        return CapabilityDataScope(
            capability_id=CAPABILITY_ID, purpose=PURPOSE,
            approved_fields=frozenset(fields), provider=self.provider_id,
            processing_mode="remote_model",
        )

    @staticmethod
    def _degraded(issue: str, *, ai_used: bool, message: str) -> dict[str, Any]:
        return {"status": "degraded", "ai_used": ai_used, "draft": issue, "message": message}

    def draft(
        self,
        citizen_issue: str,
        *,
        identity: IdentityContext,
        document_type: str,
        consent_scope: CapabilityDataScope | None,
        location_code: str | None = None,
    ) -> dict[str, Any]:
        """Return validated, editable suggestions; never persist or send a document."""
        issue = citizen_issue.strip()
        if not issue:
            return {
                "status": "invalid_input",
                "ai_used": False,
                "message": "A civic issue or existing draft is required.",
            }
        if not identity.principal.has_capability(CAPABILITY_ID):
            return {
                "status": "not_authorized",
                "ai_used": False,
                "message": "This identity is not authorized to use AI drafting.",
            }
        if not ai_settings.OPENROUTER_API_KEY or not ai_settings.LEGAL_DRAFTING_MODEL:
            return self._degraded(
                issue,
                ai_used=False,
                message="AI is not configured; the source text was left unchanged.",
            )

        regional_profile = fetch_profile_by_code(location_code or "") if location_code else None
        fields = ("citizen_issue", "regional_routing_metadata") if location_code else ("citizen_issue",)
        system = f"{_SYSTEM_PROMPT} Document type: {document_type.strip() or 'civic complaint'}."
        if regional_profile is not None:
            system += (
                f" Regional context: {regional_profile}. Treat it as contextual "
                "routing metadata, not verified legal authority."
            )
        request = AIRequest(
            purpose=PURPOSE,
            messages=(
                {"role": "system", "content": system},
                {"role": "user", "content": issue},
            ),
            model=ai_settings.LEGAL_DRAFTING_MODEL,
            data_scope=fields,
        )
        context = CapabilityExecutionContext.for_capability(
            identity,
            capability_id=CAPABILITY_ID,
            action="draft",
            surface=identity.principal.interface or "shared-capability",
        )
        try:
            generated = self._gateway.generate(
                AIExecutionRequest(
                    identity=identity,
                    execution_context=context,
                    request=request,
                    provider=self.provider_id,
                    processing_mode="remote_model",
                ),
                consent_scope=consent_scope,
            )
        except PermissionError:
            return {
                "status": "consent_required", "ai_used": False,
                "message": "Explicit consent for remote AI processing is required.",
            }
        except (requests.RequestException, ValueError, TypeError):
            return self._degraded(
                issue, ai_used=False,
                message="AI drafting failed; the source text was left unchanged.",
            )

        try:
            structured = normalize_provider_draft(
                dict(generated.payload),
                fallback_subject=issue.splitlines()[0][:200],
            )
        except InvalidAIDraftOutput:
            return self._degraded(
                issue,
                ai_used=True,
                message="AI output could not be validated; no generated sections were applied.",
            )
        return {
            "status": "available",
            "ai_used": True,
            "provider": generated.provider_id,
            "model": generated.model,
            "regional_profile": regional_profile,
            "structured_draft": structured,
        }
