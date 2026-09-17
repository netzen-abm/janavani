from __future__ import annotations

from src.capabilities.safety_privacy import (
    AccessPurpose,
    SafetyPrivacyDecision,
    SafetyPrivacyRequest,
    SensitiveResource,
    evaluate_safety_privacy,
)
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen-1",
            interface="test",
            capabilities=frozenset({"sos:trigger"}),
        )
    )


def execution_context(identity_context: IdentityContext) -> CapabilityExecutionContext:
    return CapabilityExecutionContext.for_capability(
        identity_context,
        capability_id="sos:trigger",
        action="sos:trigger",
        surface="test",
        resource_id="sos-1",
        idempotency_key="idem-sos-1",
        risk_level="high",
        side_effect_class=SideEffectClass.EXTERNAL_SIDE_EFFECT,
    )


def request(*, approved: bool) -> SafetyPrivacyRequest:
    identity_context = identity()
    return SafetyPrivacyRequest(
        identity=identity_context,
        purpose=AccessPurpose.SOS_TRANSMISSION,
        resource=SensitiveResource.FILES,
        capability="sos:trigger",
        remote_transmission=True,
        consequential_action=True,
        explicit_user_approval=approved,
        execution_context=execution_context(identity_context),
    )


def test_unapproved_consequential_sos_requires_review() -> None:
    result = evaluate_safety_privacy(request(approved=False))
    assert result.decision is SafetyPrivacyDecision.REVIEW


def test_approved_consequential_sos_is_allowed() -> None:
    result = evaluate_safety_privacy(request(approved=True))
    assert result.decision is SafetyPrivacyDecision.ALLOW
