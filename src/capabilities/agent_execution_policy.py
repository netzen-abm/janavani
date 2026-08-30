"""Policy-enforced Agentic AI execution boundary.

The agent never receives implicit authority from having access to a tool.
Every tool invocation is checked against tool scope, capability-scoped consent,
and explicit confirmation for consequential actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Optional

from .capability_consent import CapabilityConsentEvaluator, CapabilityPolicy, ConsentGrant


class ToolRisk(str, Enum):
    READ_ONLY = "READ_ONLY"
    TRANSFORMATIVE = "TRANSFORMATIVE"
    CONSEQUENTIAL = "CONSEQUENTIAL"


@dataclass(frozen=True)
class AgentTool:
    tool_id: str
    capability_id: str
    risk: ToolRisk
    allowed_fields: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class AgentExecutionRequest:
    capability_policy: CapabilityPolicy
    tool: AgentTool
    consent_grant: Optional[ConsentGrant] = None
    confirmed: bool = False


@dataclass(frozen=True)
class AgentExecutionDecision:
    allowed: bool
    reason: str
    allowed_fields: FrozenSet[str] = frozenset()
    confirmation_required: bool = False


class AgentExecutionPolicy:
    """Fail-closed policy gate for agent tool execution."""

    def __init__(self, consent_evaluator: Optional[CapabilityConsentEvaluator] = None):
        self._consent = consent_evaluator or CapabilityConsentEvaluator()

    def evaluate(self, request: AgentExecutionRequest) -> AgentExecutionDecision:
        policy = request.capability_policy
        tool = request.tool

        if tool.capability_id != policy.capability_id:
            return AgentExecutionDecision(False, "Tool is outside the requested capability scope.")

        consent = self._consent.evaluate(policy, request.consent_grant)
        if consent.decision.value in {"DENIED", "EXPIRED", "SCOPE_MISMATCH", "REQUIRED"}:
            return AgentExecutionDecision(False, f"Consent gate failed: {consent.reason}")

        if not tool.allowed_fields.issubset(consent.allowed_fields):
            return AgentExecutionDecision(False, "Tool requests data outside the granted capability scope.")

        if tool.risk == ToolRisk.CONSEQUENTIAL and not request.confirmed:
            return AgentExecutionDecision(
                False,
                "Explicit user confirmation is required for consequential tool execution.",
                allowed_fields=tool.allowed_fields,
                confirmation_required=True,
            )

        return AgentExecutionDecision(True, "Agent tool execution is within policy scope.", tool.allowed_fields)
