"""Provider-neutral composition of authorization, delegation, consent, and service policy.

This module is deliberately a policy layer above the canonical authorization kernel.
It does not replace identity, authentication, the kernel, repositories, or database RLS.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from src.access.authorization import AuthorizationDecision, AuthorizationPolicy, AuthorizationRequest
from src.core.consent import Consent
from src.identity.principal import AuthenticationMethod


@dataclass(frozen=True)
class DelegationGrant:
    """Explicit, bounded authority granted by one principal to another."""

    delegation_id: str
    grantor_id: str
    delegate_id: str
    capabilities: frozenset[str]
    actions: frozenset[str] = frozenset()
    resource_ids: frozenset[str] = frozenset()
    expires_at: str | None = None
    revoked: bool = False

    def is_active(self, *, now: datetime | None = None) -> bool:
        if self.revoked:
            return False
        if not self.delegation_id or not self.grantor_id or not self.delegate_id:
            return False
        if not self.capabilities:
            return False
        if self.expires_at is None:
            return True
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        except ValueError:
            return False
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        return current < expiry

    def authorizes(self, *, delegate_id: str, grantor_id: str, capability: str, action: str, resource_id: str | None) -> bool:
        if not self.is_active():
            return False
        if self.delegate_id != delegate_id or self.grantor_id != grantor_id:
            return False
        if capability not in self.capabilities:
            return False
        if self.actions and action not in self.actions:
            return False
        if self.resource_ids and resource_id not in self.resource_ids:
            return False
        return True


@dataclass(frozen=True)
class ServiceIdentityPolicy:
    """Explicit allow-list for service principals using service credentials."""

    allowed_capabilities: frozenset[str] = frozenset()
    allowed_actions: frozenset[str] = frozenset()

    def allows(self, *, capability: str, action: str) -> bool:
        return capability in self.allowed_capabilities and action in self.allowed_actions


@dataclass(frozen=True)
class ComposedAuthorizationRequest:
    """Authorization request plus optional delegation/consent/service policy inputs."""

    request: AuthorizationRequest
    delegation: DelegationGrant | None = None
    delegation_grantor_id: str | None = None
    consents: tuple[Consent, ...] = ()
    consent_purpose: str | None = None
    consent_scope: str | None = None
    service_policy: ServiceIdentityPolicy | None = None


class ComposedAuthorizationPolicy:
    """Evaluate the kernel first, then compose independent policy gates."""

    def __init__(self, kernel: AuthorizationPolicy | None = None) -> None:
        self._kernel = kernel or AuthorizationPolicy()

    def evaluate(self, request: ComposedAuthorizationRequest) -> AuthorizationDecision:
        decision = self._kernel.evaluate(request.request)
        if decision is AuthorizationDecision.DENY:
            return decision

        principal = request.request.context.principal
        if request.delegation is not None:
            grantor_id = request.delegation_grantor_id or request.request.resource_owner_id
            if grantor_id is None or not request.delegation.authorizes(
                delegate_id=principal.principal_id,
                grantor_id=grantor_id,
                capability=request.request.capability,
                action=request.request.action,
                resource_id=request.request.resource_id,
            ):
                return AuthorizationDecision.DENY

        if request.consent_purpose is not None or request.consent_scope is not None:
            if not request.consent_purpose or not request.consent_scope:
                return AuthorizationDecision.DENY
            if not any(
                consent.subject_id == principal.principal_id
                and consent.authorizes(request.consent_purpose, request.consent_scope)
                for consent in request.consents
            ):
                return AuthorizationDecision.DENY

        if principal.authentication_method is AuthenticationMethod.SERVICE_CREDENTIAL:
            if request.service_policy is None or not request.service_policy.allows(
                capability=request.request.capability,
                action=request.request.action,
            ):
                return AuthorizationDecision.DENY

        return decision


def authorize_composed(request: ComposedAuthorizationRequest) -> AuthorizationDecision:
    """Evaluate the canonical kernel plus the optional policy gates."""
    return ComposedAuthorizationPolicy().evaluate(request)
