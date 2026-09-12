from datetime import UTC, datetime, timedelta

from src.access.authorization import AuthorizationDecision, AuthorizationRequest
from src.access.policy_composition import ComposedAuthorizationRequest, DelegationGrant, ServiceIdentityPolicy
from src.access.policy_evaluator import RepositoryPolicyEvaluator
from src.access.policy_repository import InMemoryPolicyRepository
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


def _identity(principal_id: str = "delegate-1", *, service: bool = False) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            authentication_method=(
                AuthenticationMethod.SERVICE_CREDENTIAL if service else AuthenticationMethod.OIDC
            ),
            capabilities=frozenset({"case:submit"}),
        ),
        request_id=f"req-{principal_id}",
    )


def _request(identity: IdentityContext, **kwargs) -> AuthorizationRequest:
    values = {
        "context": identity,
        "capability": "case:submit",
        "action": "case:submit",
        "resource_id": "case-1",
    }
    values.update(kwargs)
    return AuthorizationRequest(**values)


def _delegation(*, grantor_id="citizen-1", delegate_id="delegate-1", action="case:submit", resource="case-1", revoked=False, expires_at=None):
    return DelegationGrant(
        delegation_id=f"delegation-{grantor_id}-{delegate_id}",
        grantor_id=grantor_id,
        delegate_id=delegate_id,
        capabilities=frozenset({"case:submit"}),
        actions=frozenset({action}),
        resource_ids=frozenset({resource}),
        revoked=revoked,
        expires_at=expires_at,
    )


def _consent(subject_id: str = "citizen-1", *, purpose="submit civic case", scope=("case:submit",), status=ConsentStatus.GRANTED):
    return Consent(
        consent_id=f"consent-{subject_id}-{purpose}",
        subject_id=subject_id,
        purpose=purpose,
        scope=scope,
        grant_type=ConsentGrantType.EXPLICIT,
        status=status,
        created_at="2026-09-12T00:00:00+00:00",
        revoked_at=("2026-09-12T00:01:00+00:00" if status is ConsentStatus.REVOKED else None),
    )


def test_repository_resolves_bounded_delegation_and_grantor_consent() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_delegation(_delegation())
    repo.save_consent(_consent("citizen-1"))
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        delegation_grantor_id="citizen-1",
        consent_purpose="submit civic case",
        consent_scope="case:submit",
        consent_subject_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.ALLOW


def test_cross_principal_delegation_is_denied() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_delegation(_delegation(grantor_id="citizen-2"))
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        delegation_grantor_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_revoked_delegation_is_not_resolved_as_authority() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_delegation(_delegation(revoked=True))
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        delegation_grantor_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_expired_delegation_is_not_resolved_as_authority() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_delegation(_delegation(expires_at=(datetime.now(UTC) - timedelta(minutes=1)).isoformat()))
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        delegation_grantor_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_wrong_resource_and_action_do_not_match_persisted_delegation() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_delegation(_delegation())
    identity = _identity()
    wrong_resource = ComposedAuthorizationRequest(
        request=_request(identity, resource_id="case-2"),
        delegation_grantor_id="citizen-1",
    )
    wrong_action = ComposedAuthorizationRequest(
        request=_request(identity, action="case:delete"),
        delegation_grantor_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(wrong_resource) is AuthorizationDecision.DENY
    assert RepositoryPolicyEvaluator(repo).evaluate(wrong_action) is AuthorizationDecision.DENY


def test_delegate_cannot_use_unrelated_consent() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_delegation(_delegation())
    repo.save_consent(_consent("citizen-2"))
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        delegation_grantor_id="citizen-1",
        consent_purpose="submit civic case",
        consent_scope="case:submit",
        consent_subject_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_wrong_purpose_or_scope_is_denied() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_consent(_consent("citizen-1"))
    identity = _identity("citizen-1")
    wrong_purpose = ComposedAuthorizationRequest(
        request=_request(identity), consent_purpose="other", consent_scope="case:submit"
    )
    wrong_scope = ComposedAuthorizationRequest(
        request=_request(identity), consent_purpose="submit civic case", consent_scope="case:read"
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(wrong_purpose) is AuthorizationDecision.DENY
    assert RepositoryPolicyEvaluator(repo).evaluate(wrong_scope) is AuthorizationDecision.DENY


def test_revoked_consent_is_denied() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_consent(_consent("citizen-1", status=ConsentStatus.REVOKED))
    identity = _identity("citizen-1")
    request = ComposedAuthorizationRequest(
        request=_request(identity), consent_purpose="submit civic case", consent_scope="case:submit"
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_missing_service_policy_is_denied() -> None:
    repo = InMemoryPolicyRepository()
    identity = _identity("service-1", service=True)
    request = ComposedAuthorizationRequest(request=_request(identity))
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_unlisted_service_action_is_denied() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_service_policy(
        "service-1",
        ServiceIdentityPolicy(
            allowed_capabilities=frozenset({"case:submit"}),
            allowed_actions=frozenset({"case:read"}),
        ),
    )
    identity = _identity("service-1", service=True)
    request = ComposedAuthorizationRequest(request=_request(identity))
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY


def test_matching_service_policy_is_allowed() -> None:
    repo = InMemoryPolicyRepository()
    repo.save_service_policy(
        "service-1",
        ServiceIdentityPolicy(
            allowed_capabilities=frozenset({"case:submit"}),
            allowed_actions=frozenset({"case:submit"}),
        ),
    )
    identity = _identity("service-1", service=True)
    request = ComposedAuthorizationRequest(request=_request(identity))
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.ALLOW


def test_empty_repository_state_never_elevates_authority() -> None:
    repo = InMemoryPolicyRepository()
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        delegation_grantor_id="citizen-1",
        consent_purpose="submit civic case",
        consent_scope="case:submit",
        consent_subject_id="citizen-1",
    )
    assert RepositoryPolicyEvaluator(repo).evaluate(request) is AuthorizationDecision.DENY
