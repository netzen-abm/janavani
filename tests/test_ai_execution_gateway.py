import pytest

from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy, DataClassification, DataRequirement
from src.access.scoped_execution_policy import ScopedExecutionPolicy
from src.ai.gateway import AIExecutionGateway, AIExecutionRequest
from src.ai.provider import AIRequest, AIResponse
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def identity():
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:ai-test",
            capabilities=frozenset({"civic:ai-draft"}),
        )
    )


class Provider:
    provider_id = "local"

    def __init__(self):
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        return AIResponse(provider_id=self.provider_id, model=request.model, payload={"ok": True})


def gateway(provider):
    return AIExecutionGateway(
        provider=provider,
        scoped_policy=ScopedExecutionPolicy(
            capability="civic:ai-draft",
            allowed_fields=frozenset({"citizen_issue"}),
            allowed_providers=frozenset({"local"}),
            allowed_processing_modes=frozenset({"deterministic"}),
            allowed_purposes=frozenset({"civic_document_drafting"}),
        ),
        data_scope_policy=CapabilityDataScopePolicy(
            capability_id="civic:ai-draft",
            requirements=(DataRequirement("citizen_issue", DataClassification.PERSONAL),),
        ),
    )


def execution():
    identity_context = identity()
    return CapabilityExecutionContext.for_capability(
        identity_context,
        capability_id="civic:ai-draft",
        action="draft",
        surface="web",
    )


def request():
    return AIExecutionRequest(
        identity=identity(),
        execution_context=execution(),
        request=AIRequest(
            purpose="civic_document_drafting",
            messages=({"role": "user", "content": "citizen issue"},),
            model="test-model",
            data_scope=("citizen_issue",),
            provenance_refs=("case-1",),
        ),
        provider="local",
        processing_mode="deterministic",
    )


def test_ai_provider_is_reached_only_after_exact_consent_scope():
    provider = Provider()
    g = gateway(provider)
    consent = CapabilityDataScope(
        capability_id="civic:ai-draft",
        purpose="civic_document_drafting",
        approved_fields=frozenset({"citizen_issue"}),
        provider="local",
        processing_mode="deterministic",
    )
    result = g.generate(request(), consent_scope=consent)
    assert result.payload == {"ok": True}
    assert len(provider.calls) == 1


def test_ai_provider_is_not_called_without_personal_data_consent():
    provider = Provider()
    with pytest.raises(PermissionError):
        gateway(provider).generate(request())
    assert provider.calls == []


def test_ai_provider_is_not_called_for_provider_or_field_expansion():
    provider = Provider()
    consent = CapabilityDataScope(
        capability_id="civic:ai-draft",
        purpose="civic_document_drafting",
        approved_fields=frozenset({"citizen_issue"}),
        provider="local",
        processing_mode="deterministic",
    )
    bad = request()
    bad = AIExecutionRequest(
        identity=bad.identity,
        execution_context=bad.execution_context,
        request=AIRequest(
            purpose=bad.request.purpose,
            messages=bad.request.messages,
            model=bad.request.model,
            data_scope=("secret",),
            provenance_refs=bad.request.provenance_refs,
        ),
        provider="remote",
        processing_mode="deterministic",
    )
    with pytest.raises(PermissionError):
        gateway(provider).generate(bad, consent_scope=consent)
    assert provider.calls == []
