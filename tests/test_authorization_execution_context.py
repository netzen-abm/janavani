from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def _identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(principal_id="citizen-1", capabilities=frozenset({"case:submit"})),
        request_id="req-1",
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


def test_mismatched_execution_identity_is_denied() -> None:
    identity = _identity()
    other = IdentityContext(
        principal=Principal(principal_id="citizen-2", capabilities=frozenset({"case:submit"})),
        request_id="req-2",
    )
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
        identity,
        capability_id="case:submit",
        action="case:acknowledge",
        surface="web",
    )
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability="case:submit",
        action="case:submit",
        execution_context=envelope,
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
