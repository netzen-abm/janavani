"""Policy boundary for Agentic AI tool execution.

Agent intent is never treated as authority. Each tool call must identify a
canonical capability, purpose, requested data and processing provider/mode.
"""

from dataclasses import dataclass
from typing import FrozenSet

from src.capabilities.consent_policy import (
    CapabilityPolicy,
    ConsentRequest,
    DataRequirement,
    evaluate_consent,
)


@dataclass(frozen=True)
class AgentToolRequest:
    agent_id: str
    tool: str
    capability: str
    purpose: str
    requested_fields: FrozenSet[str]
    provider: str
    processing_mode: str
    requires_confirmation: bool = False


class AgentToolDenied(PermissionError):
    """Raised when an agent tool request violates policy."""


def authorize_agent_tool(
    request: AgentToolRequest,
    policy: CapabilityPolicy,
    *,
    granted_consent: FrozenSet[ConsentRequest] = frozenset(),
) -> None:
    """Authorize a tool request using the same consent policy as users."""
    if not request.capability or not request.purpose:
        raise AgentToolDenied("agent request missing capability or purpose")

    if request.requested_fields - policy.allowed_fields:
        raise AgentToolDenied("agent requested fields outside capability policy")

    requirements = {
        field: DataRequirement(
            field=field,
            requires_consent=field in policy.consent_required_fields,
        )
        for field in request.requested_fields
    }
    result = evaluate_consent(
        policy,
        ConsentRequest(
            capability=request.capability,
            purpose=request.purpose,
            requested_fields=request.requested_fields,
            provider=request.provider,
            processing_mode=request.processing_mode,
        ),
        granted_consent=granted_consent,
    )
    if not result.allowed:
        raise AgentToolDenied(result.reason)

    if request.requires_confirmation and not result.consent:
        raise AgentToolDenied("explicit confirmation required for agent action")
