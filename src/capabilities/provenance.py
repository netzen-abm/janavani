"""Minimized, non-secret provenance for agent policy decisions."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import FrozenSet

from src.capabilities.agent_policy import AgentToolRequest


@dataclass(frozen=True)
class AgentDecisionEvent:
    event_id: str
    agent_id: str
    tool: str
    capability: str
    provider: str
    processing_mode: str
    requested_fields: FrozenSet[str]
    allowed: bool
    reason_code: str
    occurred_at: datetime


def _event_id(request: AgentToolRequest, allowed: bool, reason_code: str, occurred_at: datetime) -> str:
    material = "|".join(
        [
            request.agent_id,
            request.tool,
            request.capability,
            request.provider,
            request.processing_mode,
            ",".join(sorted(request.requested_fields)),
            str(allowed),
            reason_code,
            occurred_at.isoformat(),
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def decision_event(
    request: AgentToolRequest,
    *,
    allowed: bool,
    reason_code: str,
) -> AgentDecisionEvent:
    """Create audit metadata without storing prompts, tokens, or raw PII."""
    occurred_at = datetime.now(timezone.utc)
    return AgentDecisionEvent(
        event_id=_event_id(request, allowed, reason_code, occurred_at),
        agent_id=request.agent_id,
        tool=request.tool,
        capability=request.capability,
        provider=request.provider,
        processing_mode=request.processing_mode,
        requested_fields=request.requested_fields,
        allowed=allowed,
        reason_code=reason_code,
        occurred_at=occurred_at,
    )
