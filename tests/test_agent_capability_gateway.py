from src.access.agent_gateway import AgentCapabilityGateway, AgentGatewayDecision, AgentToolExecutionRequest
from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy, DataClassification, DataRequirement
from src.access.scoped_execution_policy import ScopedExecutionPolicy
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal


def identity(principal_id="citizen:agent-test"):
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({"case:document"}),
        )
    )


def request(**overrides):
    context = identity()
    execution = CapabilityExecutionContext.for_capability(
        context,
        capability_id="case:document",
        action="draft",
        surface="agent",
    )
    values = dict(
        agent_id="agent:document",
        agent_version="1",
        tool_id="document-builder",
        capability_id="case:document",
        purpose="prepare civic document",
        requested_fields=frozenset({"issue_type"}),
        provider="local",
        processing_mode="deterministic",
        identity=context,
        execution_context=execution,
    )
    values.update(overrides)
    return AgentToolExecutionRequest(**values)


def gateway():
    return AgentCapabilityGateway(
        scoped_policy=ScopedExecutionPolicy(
            capability="case:document",
            allowed_fields=frozenset({"issue_type", "facts"}),
            allowed_providers=frozenset({"local"}),
            allowed_processing_modes=frozenset({"deterministic"}),
            allowed_purposes=frozenset({"prepare civic document"}),
        ),
        data_scope_policy=CapabilityDataScopePolicy(
            capability_id="case:document",
            requirements=(
                DataRequirement("issue_type", DataClassification.NON_SENSITIVE),
                DataRequirement("facts", DataClassification.PERSONAL),
            ),
        ),
    )


def test_agent_request_stays_inside_existing_policy_boundaries():
    assert gateway().evaluate(request()) is AgentGatewayDecision.ALLOW


def test_agent_cannot_expand_fields_or_provider():
    assert gateway().evaluate(
        request(requested_fields=frozenset({"issue_type", "secret"}))
    ) is AgentGatewayDecision.DENY
    assert gateway().evaluate(request(provider="remote")) is AgentGatewayDecision.DENY


def test_personal_data_requires_exact_capability_scope():
    assert gateway().evaluate(
        request(requested_fields=frozenset({"facts"}))
    ) is AgentGatewayDecision.REQUIRE_CONSENT

    scope = CapabilityDataScope(
        capability_id="case:document",
        purpose="prepare civic document",
        approved_fields=frozenset({"facts"}),
        provider="local",
        processing_mode="deterministic",
    )
    assert gateway().evaluate(
        request(requested_fields=frozenset({"facts"})),
        consent_scope=scope,
    ) is AgentGatewayDecision.ALLOW


def test_agent_metadata_never_replaces_human_identity():
    other = identity("citizen:other")
    execution = CapabilityExecutionContext.for_capability(
        identity(),
        capability_id="case:document",
        action="draft",
        surface="agent",
    )
    assert gateway().evaluate(
        request(identity=other, execution_context=execution)
    ) is AgentGatewayDecision.DENY


def test_consequential_agent_request_is_not_auto_approved():
    execution = CapabilityExecutionContext.for_capability(
        identity(),
        capability_id="case:document",
        action="submit",
        surface="agent",
        idempotency_key="idem-agent-submit",
        side_effect_class="external_side_effect",
        risk_level="high",
    )
    result = gateway().evaluate(
        request(
            execution_context=execution,
            requires_consequential_approval=True,
        )
    )
    assert result is AgentGatewayDecision.REQUIRE_APPROVAL
