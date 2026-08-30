from datetime import datetime, timedelta, timezone

from src.capabilities.agent_execution_policy import (
    AgentExecutionPolicy,
    AgentExecutionRequest,
    AgentTool,
    ToolRisk,
)
from src.capabilities.capability_consent import (
    CapabilityPolicy,
    ConsentGrant,
    DataRequirement,
    DataClass,
    ProcessingMode,
)


def policy(*, consequential=False):
    return CapabilityPolicy.create(
        "ai.drafting",
        "draft civic document",
        [DataRequirement("sanitized_facts", DataClass.NON_SENSITIVE)],
        provider_id="local.ai",
        processing_mode=ProcessingMode.LOCAL,
        consent_required=True,
        consequential=consequential,
    )


def grant(p):
    return ConsentGrant(
        capability_id=p.capability_id,
        purpose=p.purpose,
        approved_fields=frozenset(p.required_fields),
        provider_id=p.provider_id,
        processing_mode=p.processing_mode,
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        grant_id="g-1",
    )


def test_agent_cannot_use_tool_outside_capability():
    p = policy()
    tool = AgentTool("submit", "submission", ToolRisk.CONSEQUENTIAL, frozenset({"sanitized_facts"}))
    decision = AgentExecutionPolicy().evaluate(AgentExecutionRequest(p, tool, grant(p), confirmed=True))
    assert decision.allowed is False


def test_agent_cannot_expand_granted_data_scope():
    p = policy()
    tool = AgentTool("draft", p.capability_id, ToolRisk.TRANSFORMATIVE, frozenset({"sanitized_facts", "phone"}))
    decision = AgentExecutionPolicy().evaluate(AgentExecutionRequest(p, tool, grant(p)))
    assert decision.allowed is False


def test_consequential_tool_requires_confirmation():
    p = policy(consequential=True)
    tool = AgentTool("submit", p.capability_id, ToolRisk.CONSEQUENTIAL, frozenset({"sanitized_facts"}))
    decision = AgentExecutionPolicy().evaluate(AgentExecutionRequest(p, tool, grant(p), confirmed=False))
    assert decision.allowed is False
    assert decision.confirmation_required is True


def test_consequential_tool_allowed_after_confirmation():
    p = policy(consequential=True)
    tool = AgentTool("submit", p.capability_id, ToolRisk.CONSEQUENTIAL, frozenset({"sanitized_facts"}))
    decision = AgentExecutionPolicy().evaluate(AgentExecutionRequest(p, tool, grant(p), confirmed=True))
    assert decision.allowed is True
