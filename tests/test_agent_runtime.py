from datetime import datetime, timedelta, timezone

from src.capabilities.agent_runtime import SharedAgentRuntime
from src.capabilities.agent_execution_policy import AgentTool, ToolRisk
from src.capabilities.capability_consent import CapabilityPolicy, ConsentGrant, DataClass, DataRequirement, ProcessingMode


class FakeProvider:
    name = "local.ai"

    def execute(self, tool, context):
        return {"tool": tool.tool_id, "context": context}


def make_policy():
    return CapabilityPolicy.create(
        "ai.drafting",
        "draft civic document",
        [DataRequirement("issue_type", DataClass.NON_SENSITIVE)],
        provider_id="local.ai",
        processing_mode=ProcessingMode.LOCAL,
        consent_required=True,
    )


def make_grant(policy):
    return ConsentGrant(
        capability_id=policy.capability_id,
        purpose=policy.purpose,
        approved_fields=frozenset(policy.required_fields),
        provider_id=policy.provider_id,
        processing_mode=policy.processing_mode,
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        grant_id="grant-1",
    )


def test_runtime_blocks_missing_consent_before_provider():
    runtime = SharedAgentRuntime()
    runtime.register(FakeProvider())
    policy = make_policy()
    tool = AgentTool("draft", policy.capability_id, ToolRisk.TRANSFORMATIVE, frozenset({"issue_type"}))
    result = runtime.execute(policy=policy, tool=tool, consent=None, context={"issue_type": "road"}, provider_id="local.ai")
    assert result.allowed is False
    assert result.reason.startswith("Consent gate failed")


def test_runtime_passes_only_policy_allowed_fields_to_provider():
    runtime = SharedAgentRuntime()
    runtime.register(FakeProvider())
    policy = make_policy()
    tool = AgentTool("draft", policy.capability_id, ToolRisk.TRANSFORMATIVE, frozenset({"issue_type"}))
    result = runtime.execute(
        policy=policy,
        tool=tool,
        consent=make_grant(policy),
        context={"issue_type": "road", "name": "PRIVATE", "phone": "PRIVATE"},
        provider_id="local.ai",
    )
    assert result.allowed is True
    assert result.output["context"] == {"issue_type": "road"}
    assert "name" not in result.audit.to_record()


def test_runtime_blocks_consequential_action_until_confirmation():
    runtime = SharedAgentRuntime()
    runtime.register(FakeProvider())
    policy = make_policy()
    tool = AgentTool("submit", policy.capability_id, ToolRisk.CONSEQUENTIAL, frozenset({"issue_type"}))
    result = runtime.execute(
        policy=policy,
        tool=tool,
        consent=make_grant(policy),
        context={"issue_type": "road"},
        provider_id="local.ai",
        confirmed=False,
    )
    assert result.allowed is False
    assert result.confirmation_required is True
