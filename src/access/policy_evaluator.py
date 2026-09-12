"""Repository-backed evaluation of composed authorization policy inputs."""
from __future__ import annotations

from dataclasses import dataclass

from src.access.authorization import AuthorizationDecision, AuthorizationPolicy
from src.access.policy_composition import (
    ComposedAuthorizationPolicy,
    ComposedAuthorizationRequest,
)
from src.access.policy_repository import PolicyRepository


@dataclass(frozen=True)
class RepositoryPolicyEvaluator:
    """Resolve persisted policy state before composed authorization evaluation."""

    repository: PolicyRepository
    kernel: AuthorizationPolicy | None = None

    def evaluate(self, request: ComposedAuthorizationRequest) -> AuthorizationDecision:
        principal = request.request.context.principal

        delegation = request.delegation
        if delegation is None and request.delegation_grantor_id is not None:
            candidates = self.repository.list_delegations_for_delegate(principal.principal_id)
            matching = tuple(
                grant
                for grant in candidates
                if grant.grantor_id == request.delegation_grantor_id
                and grant.authorizes(
                    delegate_id=principal.principal_id,
                    grantor_id=request.delegation_grantor_id,
                    capability=request.request.capability,
                    action=request.request.action,
                    resource_id=request.request.resource_id,
                )
            )
            if len(matching) != 1:
                return AuthorizationDecision.DENY
            delegation = matching[0]

        # Resolve consent only for the selected subject. Delegated execution may
        # name the grantor; ordinary execution defaults to the executing principal.
        subject_id = request.consent_subject_id or (
            delegation.grantor_id if delegation is not None else principal.principal_id
        )
        consents = request.consents
        if not consents and (request.consent_purpose is not None or request.consent_scope is not None):
            consents = self.repository.list_consents_for_subject(subject_id)

        service_policy = request.service_policy
        if service_policy is None:
            service_policy = self.repository.get_service_policy(principal.principal_id)

        resolved = ComposedAuthorizationRequest(
            request=request.request,
            delegation=delegation,
            delegation_grantor_id=request.delegation_grantor_id,
            consents=consents,
            consent_purpose=request.consent_purpose,
            consent_scope=request.consent_scope,
            consent_subject_id=request.consent_subject_id,
            service_policy=service_policy,
        )
        return ComposedAuthorizationPolicy(self.kernel).evaluate(resolved)
