"""Provider-neutral persistence contracts for composed authorization policy state.

The repository is intentionally narrower than the authorization engine: it stores
policy state and returns immutable domain objects. It does not make authorization
decisions, enforce database RLS, or become a provider-specific API.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.access.policy_composition import DelegationGrant, ServiceIdentityPolicy
from src.core.consent import Consent


@dataclass(frozen=True)
class PolicyState:
    """All durable policy inputs needed by composed authorization."""

    delegations: tuple[DelegationGrant, ...] = ()
    consents: tuple[Consent, ...] = ()
    service_policies: tuple[tuple[str, ServiceIdentityPolicy], ...] = ()

    def service_policy_for(self, principal_id: str) -> ServiceIdentityPolicy | None:
        for subject_id, policy in self.service_policies:
            if subject_id == principal_id:
                return policy
        return None


class PolicyRepository(Protocol):
    """Provider-neutral contract for durable composed-policy state."""

    def save_delegation(self, delegation: DelegationGrant) -> None: ...

    def get_delegation(self, delegation_id: str) -> DelegationGrant | None: ...

    def list_delegations_for_delegate(self, delegate_id: str) -> tuple[DelegationGrant, ...]: ...

    def save_consent(self, consent: Consent) -> None: ...

    def get_consent(self, consent_id: str) -> Consent | None: ...

    def list_consents_for_subject(self, subject_id: str) -> tuple[Consent, ...]: ...

    def save_service_policy(self, principal_id: str, policy: ServiceIdentityPolicy) -> None: ...

    def get_service_policy(self, principal_id: str) -> ServiceIdentityPolicy | None: ...


class InMemoryPolicyRepository:
    """Deterministic reference adapter for tests and local development."""

    def __init__(self) -> None:
        self._delegations: dict[str, DelegationGrant] = {}
        self._consents: dict[str, Consent] = {}
        self._service_policies: dict[str, ServiceIdentityPolicy] = {}

    def save_delegation(self, delegation: DelegationGrant) -> None:
        if not delegation.delegation_id:
            raise ValueError("delegation_id must not be empty")
        self._delegations[delegation.delegation_id] = delegation

    def get_delegation(self, delegation_id: str) -> DelegationGrant | None:
        return self._delegations.get(delegation_id)

    def list_delegations_for_delegate(self, delegate_id: str) -> tuple[DelegationGrant, ...]:
        return tuple(
            delegation
            for delegation in self._delegations.values()
            if delegation.delegate_id == delegate_id
        )

    def save_consent(self, consent: Consent) -> None:
        self._consents[consent.consent_id] = consent

    def get_consent(self, consent_id: str) -> Consent | None:
        return self._consents.get(consent_id)

    def list_consents_for_subject(self, subject_id: str) -> tuple[Consent, ...]:
        return tuple(consent for consent in self._consents.values() if consent.subject_id == subject_id)

    def save_service_policy(self, principal_id: str, policy: ServiceIdentityPolicy) -> None:
        if not principal_id:
            raise ValueError("principal_id must not be empty")
        self._service_policies[principal_id] = policy

    def get_service_policy(self, principal_id: str) -> ServiceIdentityPolicy | None:
        return self._service_policies.get(principal_id)

    def snapshot(self) -> PolicyState:
        """Return an immutable snapshot useful for deterministic evaluation/tests."""
        return PolicyState(
            delegations=tuple(self._delegations.values()),
            consents=tuple(self._consents.values()),
            service_policies=tuple(self._service_policies.items()),
        )
