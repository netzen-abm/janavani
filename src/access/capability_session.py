"""Provider-neutral lifecycle for purpose-bound sensitive capability access.

This module owns application-level session state only. Platform permission APIs,
OS revocation, and resource mechanics remain surface/provider responsibilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilitySessionState(str, Enum):
    NOT_REQUESTED = "not_requested"
    PURPOSE_PRESENTED = "purpose_presented"
    GRANTED = "granted"
    ACTIVE = "active"
    PURPOSE_COMPLETE = "purpose_complete"
    RELEASED = "released"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"


class CapabilitySessionError(RuntimeError):
    """Raised when a session lifecycle transition is invalid."""


@dataclass(frozen=True)
class CapabilitySession:
    session_id: str
    principal_id: str
    purpose: str
    resource: str
    state: CapabilitySessionState = CapabilitySessionState.NOT_REQUESTED


class CapabilitySessionManager:
    """Deterministic, terminal lifecycle for one purpose-bound resource use."""

    _TRANSITIONS = {
        CapabilitySessionState.NOT_REQUESTED: {
            CapabilitySessionState.PURPOSE_PRESENTED,
        },
        CapabilitySessionState.PURPOSE_PRESENTED: {
            CapabilitySessionState.GRANTED,
            CapabilitySessionState.DENIED,
            CapabilitySessionState.UNAVAILABLE,
        },
        CapabilitySessionState.GRANTED: {
            CapabilitySessionState.ACTIVE,
            CapabilitySessionState.RELEASED,
        },
        CapabilitySessionState.ACTIVE: {
            CapabilitySessionState.PURPOSE_COMPLETE,
            CapabilitySessionState.RELEASED,
        },
        CapabilitySessionState.PURPOSE_COMPLETE: {
            CapabilitySessionState.RELEASED,
        },
        CapabilitySessionState.DENIED: set(),
        CapabilitySessionState.UNAVAILABLE: set(),
        CapabilitySessionState.RELEASED: set(),
    }

    def transition(
        self,
        session: CapabilitySession,
        target: CapabilitySessionState,
    ) -> CapabilitySession:
        if not session.session_id or not session.principal_id:
            raise CapabilitySessionError("Session identity is required")
        if not session.purpose.strip() or not session.resource.strip():
            raise CapabilitySessionError("Purpose and resource are required")
        if target not in self._TRANSITIONS[session.state]:
            raise CapabilitySessionError(
                f"Invalid capability-session transition: "
                f"{session.state.value} -> {target.value}"
            )
        return CapabilitySession(
            session_id=session.session_id,
            principal_id=session.principal_id,
            purpose=session.purpose,
            resource=session.resource,
            state=target,
        )

    def present_purpose(self, session: CapabilitySession) -> CapabilitySession:
        return self.transition(session, CapabilitySessionState.PURPOSE_PRESENTED)

    def grant(self, session: CapabilitySession) -> CapabilitySession:
        return self.transition(session, CapabilitySessionState.GRANTED)

    def activate(self, session: CapabilitySession) -> CapabilitySession:
        return self.transition(session, CapabilitySessionState.ACTIVE)

    def purpose_complete(self, session: CapabilitySession) -> CapabilitySession:
        return self.transition(session, CapabilitySessionState.PURPOSE_COMPLETE)

    def release(self, session: CapabilitySession) -> CapabilitySession:
        return self.transition(session, CapabilitySessionState.RELEASED)
