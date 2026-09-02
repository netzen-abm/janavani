from src.access.authorization import (
    AuthorizationDecision,
    AuthorizationPolicy,
    AuthorizationRequest,
)
from src.identity.context import anonymous_context
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.identity.context import IdentityContext


def context_with_capabilities(*capabilities: str) -> IdentityContext:
    principal = Principal(
        principal_id="citizen-1",
        identity_mode=IdentityMode.AUTHENTICATED,
        interface="test",
        authentication_method=AuthenticationMethod.PASSKEY,
        capabilities=list(capabilities),
    )
    return IdentityContext(principal=principal)


def request(context: IdentityContext, **kwargs) -> AuthorizationRequest:
    return AuthorizationRequest(
        context=context,
        capability="case",
        action="read",
        **kwargs,
    )


def test_capability_grants_access():
    decision = AuthorizationPolicy().evaluate(request(context_with_capabilities("case")))
    assert decision is AuthorizationDecision.ALLOW


def test_missing_capability_denies_access():
    decision = AuthorizationPolicy().evaluate(request(context_with_capabilities()))
    assert decision is AuthorizationDecision.DENY


def test_anonymous_context_cannot_access_protected_capability():
    decision = AuthorizationPolicy().evaluate(request(anonymous_context()))
    assert decision is AuthorizationDecision.DENY


def test_high_risk_requires_approval_even_with_capability():
    decision = AuthorizationPolicy().evaluate(
        request(context_with_capabilities("case"), risk_level="high")
    )
    assert decision is AuthorizationDecision.REQUIRE_APPROVAL


def test_explicit_approval_gate_requires_approval():
    decision = AuthorizationPolicy().evaluate(
        request(context_with_capabilities("case"), requires_approval=True)
    )
    assert decision is AuthorizationDecision.REQUIRE_APPROVAL


def test_missing_capability_wins_over_approval_requirement():
    decision = AuthorizationPolicy().evaluate(
        request(context_with_capabilities(), requires_approval=True)
    )
    assert decision is AuthorizationDecision.DENY
