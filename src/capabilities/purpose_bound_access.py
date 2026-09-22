"""Provider- and surface-neutral lifecycle for purpose-bound sensitive resources."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4
from typing import Protocol


class SensitiveResourceAdapter(Protocol):
    """Surface adapter hook for stopping/closing the platform resource."""
    def release(self, *, session_id: str, resource: SensitiveResource) -> None: ...


class SensitiveDataMinimizer(Protocol):
    """Hook for applying retention/minimisation rules at purpose completion."""
    def minimize(self, *, session_id: str, resource: SensitiveResource, purpose: AccessPurpose) -> None: ...
from src.capabilities.safety_privacy import AccessPurpose, SensitiveResource
from src.identity.context import IdentityContext

class PermissionLifecycleState(str, Enum):
    NOT_REQUESTED="not_requested"; PURPOSE_PRESENTED="purpose_presented"; GRANTED="granted"; ACTIVE="active"; PURPOSE_COMPLETE="purpose_complete"; RELEASED="released"; DENIED="denied"; UNAVAILABLE="unavailable"

@dataclass(frozen=True)
class PurposeBoundPermissionRequest:
    identity: IdentityContext
    purpose: AccessPurpose
    resource: SensitiveResource
    explanation: str

@dataclass(frozen=True)
class PurposeBoundPermissionSession:
    session_id: str
    identity_id: str
    purpose: AccessPurpose
    resource: SensitiveResource
    state: PermissionLifecycleState = PermissionLifecycleState.NOT_REQUESTED

class PurposeBoundPermissionLifecycle:
    """Enforces application-level activation, completion and release."""
    def __init__(self) -> None:
        self._sessions: dict[str, PurposeBoundPermissionSession] = {}

    def present(self, request: PurposeBoundPermissionRequest) -> PurposeBoundPermissionSession:
        if not request.explanation.strip(): raise ValueError("A purpose explanation is required")
        s=PurposeBoundPermissionSession(f"perm_{uuid4().hex}",request.identity.principal.principal_id,request.purpose,request.resource,PermissionLifecycleState.PURPOSE_PRESENTED)
        self._sessions[s.session_id]=s; return s

    def grant(self, session_id: str) -> PurposeBoundPermissionSession:
        return self._transition(session_id, PermissionLifecycleState.PURPOSE_PRESENTED, PermissionLifecycleState.GRANTED)

    def activate(self, session_id: str, *, identity: IdentityContext) -> PurposeBoundPermissionSession:
        return self._transition_owned(session_id, identity, PermissionLifecycleState.GRANTED, PermissionLifecycleState.ACTIVE)

    def purpose_complete(self, session_id: str, *, identity: IdentityContext) -> PurposeBoundPermissionSession:
        return self._transition_owned(session_id, identity, PermissionLifecycleState.ACTIVE, PermissionLifecycleState.PURPOSE_COMPLETE)

    def release(self, session_id: str, *, identity: IdentityContext) -> PurposeBoundPermissionSession:
        return self._transition_owned(session_id, identity, PermissionLifecycleState.PURPOSE_COMPLETE, PermissionLifecycleState.RELEASED)

    def deny(self, session_id: str, *, identity: IdentityContext) -> PurposeBoundPermissionSession:
        return self._owned_terminal(session_id, identity, {PermissionLifecycleState.PURPOSE_PRESENTED,PermissionLifecycleState.GRANTED}, PermissionLifecycleState.DENIED)

    def unavailable(self, session_id: str, *, identity: IdentityContext) -> PurposeBoundPermissionSession:
        return self._owned_terminal(session_id, identity, {PermissionLifecycleState.PURPOSE_PRESENTED,PermissionLifecycleState.GRANTED}, PermissionLifecycleState.UNAVAILABLE)

    def get(self, session_id: str) -> PurposeBoundPermissionSession | None: return self._sessions.get(session_id)

    def _require(self, sid: str) -> PurposeBoundPermissionSession:
        s=self._sessions.get(sid)
        if s is None: raise LookupError("Permission session not found")
        return s

    def _transition(self,sid:str,expected:PermissionLifecycleState,target:PermissionLifecycleState):
        s=self._require(sid)
        if s.state is not expected: raise ValueError(f"Expected state {expected.value}, found {s.state.value}")
        return self._set(s,target)

    def _transition_owned(self,sid,identity,expected,target):
        s=self._require(sid); self._check_identity(s,identity)
        if s.state is not expected: raise ValueError(f"Expected state {expected.value}, found {s.state.value}")
        return self._set(s,target)

    def _owned_terminal(self,sid,identity,allowed,target):
        s=self._require(sid); self._check_identity(s,identity)
        if s.state not in allowed: raise ValueError("Permission can only be denied/unavailable before activation")
        return self._set(s,target)

    def _check_identity(self,s,identity):
        if s.identity_id != identity.principal.principal_id: raise PermissionError("Permission session belongs to a different identity")

    def _set(self,s,state):
        u=PurposeBoundPermissionSession(s.session_id,s.identity_id,s.purpose,s.resource,state)
        self._sessions[s.session_id]=u; return u
