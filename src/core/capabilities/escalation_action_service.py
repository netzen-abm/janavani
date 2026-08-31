"""Shared escalation action boundary.

This service converts an already-verified escalation decision into a proposed
case action. It does not submit or transmit anything and requires explicit
user confirmation before document preparation can proceed.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.core.capabilities.escalation_resolver import EscalationDecision
from src.core.contracts.authority_discovery import AuthorityStatus


@dataclass(frozen=True)
class EscalationActionProposal:
    action_type: str
    route_id: str
    authority_id: str
    authority_name: str
    reason: str
    requires_user_confirmation: bool = True


class SharedEscalationActionService:
    def propose(self, decision: EscalationDecision) -> EscalationActionProposal:
        authority = decision.authority
        if authority.status != AuthorityStatus.VERIFIED:
            raise ValueError("escalation action requires a verified destination authority")
        if not authority.source_ids:
            raise ValueError("escalation action requires authority provenance")
        return EscalationActionProposal(
            action_type="escalation",
            route_id=decision.route_id,
            authority_id=authority.authority_id,
            authority_name=authority.name,
            reason=decision.reason,
        )
