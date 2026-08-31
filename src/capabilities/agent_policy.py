"""Policy boundary for Agentic AI tool execution.

Agent intent is never treated as authority. Each tool call must identify a
canonical capability, purpose, requested data and processing provider/mode.
"""

from dataclasses import dataclass
from typing import FrozenSet

from src.capabilities.consent_policy import (
    CapabilityPolicy,
    ConsentRequest,
    ConsentScope,
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
    """Authorize an agent tool request using the shared consent policy."""
    if not request.capability or not request.purpose.strip():
        raise AgentToolDenied("agent request missing capability or purpose")

    requirements = policy.requirement_map()
    if request.requested_fields - requirements.keys():
        raise AgentToolDenied("agent requested fields outside capability policy")

    consent_scope = None
    for consent in granted_consent:
        if (
            consent.capability_id == request.capability
            and consent.purpose == request.purpose
            and consent.provider == request.provider
            and consent.processing_mode == request.processing_mode
            and set(request.requested_fields).issubset(set(consent.requested_data))
        ):
            consent_scope = ConsentScope(
                capability_id=consent.capability_id,
                purpose=consent.purpose,
                approved_data=frozenset(consent.requested_data),
                provider=consent.provider,
                processing_mode=consent.processing_mode,
            )
            break

    result = evaluate_consent(
        ConsentRequest(
            capability_id=request.capability,
            purpose=request.purpose,
            requested_data=tuple(sorted(request.requested_fields)),
            provider=request.provider,
            processing_mode=request.processing_mode,
            consequential_action=request.requires_confirmation,
        ),
        policy,
        consent_scope,
    )

    if result.value != "ALLOW":
        raise AgentToolDenied(f"agent tool request: {result.value}")
