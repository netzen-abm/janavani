"""Canonical policy gateway for agentic capability execution.

This boundary composes existing authorization, scoped execution, data-scope,
consent, and consequential-operation controls. It does not create a second
authorization or consent authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy
from src.access.consequential import ConsequentialOperationGate
from src.access.scoped_execution_policy import ScopedExecutionPolicy, ScopedExecutionRequest
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext


class AgentGatewayDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONSENT = "require_consent"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class AgentToolExecutionRequest:
    agent_id: str
    agent_version: str
    tool_id: str
    capability_id: str
    purpose: str
    requested_fields: frozenset[str]
    provider: str
    processing_mode: str
    identity: IdentityContext
    execution_context: CapabilityExecutionContext
    requires_consequential_approval: bool = False


class AgentCapabilityGateway:
    """Mandatory agent-to-capability policy boundary."""

    def __init__(
        self,
        *,
        scoped_policy: ScopedExecutionPolicy,
        data_scope_policy: CapabilityDataScopePolicy | None = None,
        consequential_gate: ConsequentialOperationGate | None = None,
    ) -> None:
        self._scoped_policy = scoped_policy
        self._data_scope_policy = data_scope_policy
        self._consequential_gate = consequential_gate or ConsequentialOperationGate()

    def evaluate(
        self,
        request: AgentToolExecutionRequest,
        *,
        consent_scope: CapabilityDataScope | None = None,
    ) -> AgentGatewayDecision:
        """Fail closed unless the agent request is provably within scope."""
        if not request.agent_id.strip() or not request.agent_version.strip() or not request.tool_id.strip():
            return AgentGatewayDecision.DENY

        if request.execution_context.identity.principal.principal_id != request.identity.principal.principal_id:
            return AgentGatewayDecision.DENY
        if request.execution_context.capability_id != request.capability_id:
            return AgentGatewayDecision.DENY

        scoped_request = ScopedExecutionRequest(
            capability=request.capability_id,
            purpose=request.purpose,
            requested_fields=request.requested_fields,
            provider=request.provider,
            processing_mode=request.processing_mode,
        )
        if not self._scoped_policy.allows(scoped_request):
            return AgentGatewayDecision.DENY

        if self._data_scope_policy is not None:
            decision = self._data_scope_policy.evaluate(
                purpose=request.purpose,
                requested_fields=request.requested_fields,
                provider=request.provider,
                processing_mode=request.processing_mode,
                consent_scope=consent_scope,
            )
            if decision.value == "deny":
                return AgentGatewayDecision.DENY
            if decision.value == "require_consent":
                return AgentGatewayDecision.REQUIRE_CONSENT

        if request.requires_consequential_approval:
            if not request.execution_context.requires_explicit_approval():
                return AgentGatewayDecision.DENY
            return AgentGatewayDecision.REQUIRE_APPROVAL

        return AgentGatewayDecision.ALLOW
