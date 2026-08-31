"""Shared escalation resolver based on verified procedure routes.

The resolver never infers that an authority is 'higher' merely by title. A
procedure provider supplies explicit escalation routes, and every destination
must be independently verified before it can be used for document addressing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus


@dataclass(frozen=True)
class EscalationRoute:
    route_id: str
    source_procedure_id: str
    from_authority_id: str
    to_authority: AuthorityCandidate
    reason: str
    verified: bool = False


class EscalationRouteProvider(Protocol):
    def routes_for(self, procedure_id: str, from_authority_id: str) -> Iterable[EscalationRoute]: ...


@dataclass(frozen=True)
class EscalationDecision:
    route_id: str
    authority: AuthorityCandidate
    reason: str
    requires_user_confirmation: bool = True


class SharedEscalationResolver:
    def __init__(self, provider: EscalationRouteProvider):
        self.provider = provider

    def resolve(self, *, procedure_id: str, from_authority_id: str) -> tuple[EscalationDecision, ...]:
        if not procedure_id.strip() or not from_authority_id.strip():
            raise ValueError("procedure_id and from_authority_id are required")
        decisions: list[EscalationDecision] = []
        for route in self.provider.routes_for(procedure_id, from_authority_id):
            if not route.verified:
                continue
            if route.to_authority.status != AuthorityStatus.VERIFIED:
                continue
            decisions.append(EscalationDecision(route.route_id, route.to_authority, route.reason))
        return tuple(decisions)
