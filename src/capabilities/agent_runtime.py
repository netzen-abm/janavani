"""Shared runtime facade that makes Agentic AI policy checks mandatory.

Access surfaces call this facade rather than provider implementations. It
combines capability-scoped consent, tool scope/risk policy, and minimized audit
records. Provider invocation occurs only after every gate passes.
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol

from .agent_audit import AgentDecision, make_agent_audit_event
from .agent_execution_policy import AgentExecutionDecision, AgentExecutionPolicy, AgentExecutionRequest, AgentTool
from .capability_consent import CapabilityPolicy, ConsentGrant


class AgentProvider(Protocol):
    name: str

    def execute(self, tool: AgentTool, context: dict[str, Any]) -> Any: ...


@dataclass(frozen=True)
class AgentRuntimeResult:
    allowed: bool
    output: Any = None
    audit: Any = None
    reason: str = ""
    confirmation_required: bool = False


class SharedAgentRuntime:
    """Single shared execution gate for all Janavani access surfaces."""

    def __init__(self, policy: Optional[AgentExecutionPolicy] = None):
        self._policy = policy or AgentExecutionPolicy()
        self._providers: dict[str, AgentProvider] = {}

    def register(self, provider: AgentProvider) -> None:
        self._providers[provider.name] = provider

    def execute(
        self,
        *,
        policy: CapabilityPolicy,
        tool: AgentTool,
        consent: Optional[ConsentGrant],
        context: dict[str, Any],
        provider_id: str,
        confirmed: bool = False,
    ) -> AgentRuntimeResult:
        request = AgentExecutionRequest(
            capability_policy=policy,
            tool=tool,
            consent_grant=consent,
            confirmed=confirmed,
        )
        decision = self._policy.evaluate(request)
        decision_kind = AgentDecision.ALLOWED if decision.allowed else (
            AgentDecision.CONFIRMATION_REQUIRED if decision.confirmation_required else AgentDecision.BLOCKED
        )
        audit = make_agent_audit_event(
            capability_id=policy.capability_id,
            tool_id=tool.tool_id,
            decision=decision_kind,
            risk=tool.risk.value,
            reason=decision.reason,
            consent_grant_id=consent.grant_id if consent else None,
            provider_id=provider_id,
            confirmation_required=decision.confirmation_required,
            confirmation_obtained=confirmed,
        )
        if not decision.allowed:
            return AgentRuntimeResult(
                allowed=False,
                audit=audit,
                reason=decision.reason,
                confirmation_required=decision.confirmation_required,
            )

        provider = self._providers.get(provider_id)
        if provider is None:
            blocked_audit = make_agent_audit_event(
                capability_id=policy.capability_id,
                tool_id=tool.tool_id,
                decision=AgentDecision.BLOCKED,
                risk=tool.risk.value,
                reason="unknown_provider",
                consent_grant_id=consent.grant_id if consent else None,
                provider_id=provider_id,
            )
            return AgentRuntimeResult(False, audit=blocked_audit, reason="unknown_provider")

        output = provider.execute(tool, {key: context[key] for key in decision.allowed_fields if key in context})
        return AgentRuntimeResult(True, output=output, audit=audit, reason=decision.reason)
