from datetime import datetime, timedelta, timezone

from src.access.authorization import AuthorizationDecision, AuthorizationRequest
from src.access.policy_composition import (
    ComposedAuthorizationRequest,
    DelegationGrant,
    ServiceIdentityPolicy,
    authorize_composed,
)
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


def _identity(
    principal_id: str = "citizen-1",
    *,
    capabilities: set[str] | None = None,
    service: bool = False,
) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            authentication_method=(
                AuthenticationMethod.SERVICE_CREDENTIAL
                if service
                else AuthenticationMethod.OIDC
            ),
            capabilities=frozenset({"case:submit"} if capabilities is None else capabilities),
        ),
        request_id=f"req-{principal_id}",
    )


def _request(identity: IdentityContext, **kwargs) -> AuthorizationRequest:
    values = {
        "context": identity,
        "capability": "case:submit",
        "action": "case:submit",
        "resource_id": "case-1",
        "resource_owner_id": identity.principal.principal_id,
    }
    values.update(kwargs)
    return AuthorizationRequest(**values)


def _consent(subject_id: str = "citizen-1") -> Consent:
    return Consent(
        consent_id="consent-1",
        subject_id=subject_id,
        purpose="submit civic case",
        scope=("case:submit",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-12T00:00:00+00:00",
    )


def _delegation(*, expires_at: str | None = None, revoked: bool = False) -> DelegationGrant:
    return DelegationGrant(
        delegation_id="delegation-1",
        grantor_id="citizen-1",
        delegate_id="delegate-1",
        capabilities=frozenset({"case:submit"}),
        actions=frozenset({"case:submit"}),
        resource_ids=frozenset({"case-1"}),
        expires_at=expires_at,
        revoked=revoked,
    )


def test_delegated_operation_is_allowed_when_explicitly_bounded() -> None:
    identity = _identity("delegate-1")
    request = _request(identity, resource_owner_id=None)
    composed = ComposedAuthorizationRequest(
        request=request,
        delegation=_delegation(),
        delegation_grantor_id="citizen-1",
    )
    assert authorize_composed(composed) is AuthorizationDecision.ALLOW


def test_revoked_delegation_is_denied() -> None:
    identity = _identity("delegate-1")
    composed = ComposedAuthorizationRequest(
        request=_request(identity, resource_owner_id=None),
        delegation=_delegation(revoked=True),
        delegation_grantor_id="citizen-1",
    )
    assert authorize_composed(composed) is AuthorizationDecision.DENY


def test_expired_delegation_is_denied() -> None:
    expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    identity = _identity("delegate-1")
    composed = ComposedAuthorizationRequest(
        request=_request(identity, resource_owner_id=None),
        delegation=_delegation(expires_at=expired),
        delegation_grantor_id="citizen-1",
    )
    assert authorize_composed(composed) is AuthorizationDecision.DENY


def test_delegation_cannot_expand_capability() -> None:
    identity = _identity("delegate-1", capabilities={"case:read"})
    composed = ComposedAuthorizationRequest(
        request=_request(identity, resource_owner_id=None),
        delegation=_delegation(),
        delegation_grantor_id="citizen-1",
    )
    assert authorize_composed(composed) is AuthorizationDecision.DENY


def test_delegation_cannot_escape_resource_scope() -> None:
    identity = _identity("delegate-1")
    request = AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        resource_id="case-2",
    )
    composed = ComposedAuthorizationRequest(
        request=request,
        delegation=_delegation(),
        delegation_grantor_id="citizen-1",
    )
    assert authorize_composed(composed) is AuthorizationDecision.DENY


def test_purpose_bound_consent_is_required_when_requested() -> None:
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        consents=(_consent(),),
        consent_purpose="submit civic case",
        consent_scope="case:submit",
    )
    assert authorize_composed(request) is AuthorizationDecision.ALLOW


def test_wrong_consent_purpose_is_denied() -> None:
    identity = _identity()
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        consents=(_consent(),),
        consent_purpose="different purpose",
        consent_scope="case:submit",
    )
    assert authorize_composed(request) is AuthorizationDecision.DENY


def test_revoked_consent_is_denied() -> None:
    identity = _identity()
    consent = _consent()
    revoked = Consent(
        consent_id=consent.consent_id,
        subject_id=consent.subject_id,
        purpose=consent.purpose,
        scope=consent.scope,
        grant_type=consent.grant_type,
        status=ConsentStatus.REVOKED,
        created_at=consent.created_at,
        revoked_at="2026-09-12T00:01:00+00:00",
    )
    request = ComposedAuthorizationRequest(
        request=_request(identity),
        consents=(revoked,),
        consent_purpose="submit civic case",
        consent_scope="case:submit",
    )
    assert authorize_composed(request) is AuthorizationDecision.DENY


def test_service_identity_requires_explicit_service_policy() -> None:
    identity = _identity(service=True)
    composed = ComposedAuthorizationRequest(request=_request(identity))
    assert authorize_composed(composed) is AuthorizationDecision.DENY


def test_service_identity_allow_list_can_authorize() -> None:
    identity = _identity(service=True)
    composed = ComposedAuthorizationRequest(
        request=_request(identity),
        service_policy=ServiceIdentityPolicy(
            allowed_capabilities=frozenset({"case:submit"}),
            allowed_actions=frozenset({"case:submit"}),
        ),
    )
    assert authorize_composed(composed) is AuthorizationDecision.ALLOW


def test_service_identity_cannot_use_unlisted_action() -> None:
    identity = _identity(service=True)
    composed = ComposedAuthorizationRequest(
        request=_request(identity),
        service_policy=ServiceIdentityPolicy(
            allowed_capabilities=frozenset({"case:submit"}),
            allowed_actions=frozenset({"case:read"}),
        ),
    )
    assert authorize_composed(composed) is AuthorizationDecision.DENY


def test_base_authorization_denial_wins_over_composed_gates() -> None:
    identity = _identity(capabilities=set())
    composed = ComposedAuthorizationRequest(
        request=_request(identity),
        consents=(_consent(),),
        consent_purpose="submit civic case",
        consent_scope="case:submit",
        service_policy=ServiceIdentityPolicy(
            allowed_capabilities=frozenset({"case:submit"}),
            allowed_actions=frozenset({"case:submit"}),
        ),
    )
    assert authorize_composed(composed) is AuthorizationDecision.DENY
