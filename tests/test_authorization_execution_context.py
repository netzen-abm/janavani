from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def _identity(principal_id: str = "citizen-1", *, capabilities=None) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            capabilities=frozenset(capabilities or {"case:submit"}),
        ),
        request_id=f"req-{principal_id}",
    )


def _context(identity: IdentityContext, **kwargs) -> CapabilityExecutionContext:
    return CapabilityExecutionContext.for_capability(
        identity,
        capability_id="case:submit",
        action="case:submit",
        surface="web",
        **kwargs,
    )


def test_matching_execution_context_is_authorized() -> None:
    identity = _identity()
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        resource_id="case-1",
        execution_context=_context(identity, resource_id="case-1"),
    ))
    assert decision is AuthorizationDecision.ALLOW


def test_missing_capability_is_denied() -> None:
    identity = _identity(capabilities=set())
    decision = authorize(AuthorizationRequest(
        context=identity, capability="case:submit", action="case:submit"
    ))
    assert decision is AuthorizationDecision.DENY


def test_cross_principal_resource_owner_is_denied() -> None:
    identity = _identity("citizen-1")
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        resource_id="case-2",
        resource_owner_id="citizen-2",
    ))
    assert decision is AuthorizationDecision.DENY


def test_matching_resource_owner_is_allowed() -> None:
    identity = _identity("citizen-1")
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        resource_id="case-1",
        resource_owner_id="citizen-1",
    ))
    assert decision is AuthorizationDecision.ALLOW


def test_mismatched_execution_identity_is_denied() -> None:
    identity = _identity("citizen-1")
    other = _identity("citizen-2")
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        execution_context=_context(other),
    ))
    assert decision is AuthorizationDecision.DENY


def test_mismatched_execution_action_is_denied() -> None:
    identity = _identity()
    envelope = CapabilityExecutionContext.for_capability(
        identity, capability_id="case:submit", action="case:acknowledge", surface="web"
    )
    decision = authorize(AuthorizationRequest(
        context=identity, capability="case:submit", action="case:submit", execution_context=envelope
    ))
    assert decision is AuthorizationDecision.DENY


def test_mismatched_execution_resource_is_denied() -> None:
    identity = _identity()
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        resource_id="case-1",
        execution_context=_context(identity, resource_id="case-2"),
    ))
    assert decision is AuthorizationDecision.DENY


def test_mismatched_execution_risk_is_denied() -> None:
    identity = _identity()
    envelope = _context(identity, risk_level="normal")
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        risk_level="high",
        execution_context=envelope,
    ))
    assert decision is AuthorizationDecision.DENY


def test_approval_request_cannot_use_read_only_execution_context() -> None:
    identity = _identity()
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        requires_approval=True,
        execution_context=_context(identity, side_effect_class=SideEffectClass.READ),
    ))
    assert decision is AuthorizationDecision.DENY


def test_high_risk_operation_requires_approval() -> None:
    identity = _identity()
    decision = authorize(AuthorizationRequest(
        context=identity, capability="case:submit", action="case:submit", risk_level="high"
    ))
    assert decision is AuthorizationDecision.REQUIRE_APPROVAL


def test_missing_capability_cannot_be_overridden_by_approval() -> None:
    identity = _identity(capabilities=set())
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        requires_approval=True,
    ))
    assert decision is AuthorizationDecision.DENY
