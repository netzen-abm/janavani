"""Shared minimized provenance events for AI/agent policy decisions."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
import uuid


class AgentDecision(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"


@dataclass(frozen=True)
class AgentAuditEvent:
    event_id: str
    capability_id: str
    tool_id: str
    decision: AgentDecision
    risk: str
    consent_grant_id: Optional[str]
    provider_id: Optional[str]
    confirmation_required: bool
    confirmation_obtained: bool
    timestamp: str
    reason: str

    def to_record(self) -> Mapping[str, Any]:
        return asdict(self)


def make_agent_audit_event(
    *,
    capability_id: str,
    tool_id: str,
    decision: AgentDecision,
    risk: str,
    reason: str,
    consent_grant_id: Optional[str] = None,
    provider_id: Optional[str] = None,
    confirmation_required: bool = False,
    confirmation_obtained: bool = False,
) -> AgentAuditEvent:
    return AgentAuditEvent(
        event_id=f"agent-{uuid.uuid4().hex[:16]}",
        capability_id=capability_id,
        tool_id=tool_id,
        decision=decision,
        risk=risk,
        consent_grant_id=consent_grant_id,
        provider_id=provider_id,
        confirmation_required=confirmation_required,
        confirmation_obtained=confirmation_obtained,
        timestamp=datetime.now(timezone.utc).isoformat(),
        reason=reason,
    )
