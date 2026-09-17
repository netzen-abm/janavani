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


def context() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="test-principal",
            interface="test",
            capabilities=frozenset({"safety:privacy"}),
        )
    )


def request(**overrides: object) -> SafetyPrivacyRequest:
    values: dict[str, object] = {
        "identity": context(),
        "purpose": AccessPurpose.EVIDENCE_CAPTURE,
        "resource": SensitiveResource.CAMERA,
    }
    values.update(overrides)
    return SafetyPrivacyRequest(**values)  # type: ignore[arg-type]


def test_allows_purpose_bound_minimized_camera_access() -> None:
    result = evaluate_safety_privacy(request())
    assert result.decision is SafetyPrivacyDecision.ALLOW


def test_blocks_without_explicit_user_choice() -> None:
    result = evaluate_safety_privacy(request(explicit_user_choice=False))
    assert result.decision is SafetyPrivacyDecision.BLOCK


def test_blocks_background_sensitive_access() -> None:
    result = evaluate_safety_privacy(request(background_access=True))
    assert result.decision is SafetyPrivacyDecision.BLOCK


def test_blocks_continuous_sensitive_access() -> None:
    result = evaluate_safety_privacy(request(continuous_access=True))
    assert result.decision is SafetyPrivacyDecision.BLOCK


def test_blocks_remote_transmission_without_explicit_transmission_purpose() -> None:
    result = evaluate_safety_privacy(request(remote_transmission=True))
    assert result.decision is SafetyPrivacyDecision.BLOCK


def test_allows_remote_transmission_for_explicit_upload() -> None:
    result = evaluate_safety_privacy(
        request(purpose=AccessPurpose.EXPLICIT_UPLOAD, remote_transmission=True)
    )
    assert result.decision is SafetyPrivacyDecision.ALLOW


def test_allows_remote_transmission_for_sos_transmission() -> None:
    result = evaluate_safety_privacy(
        request(purpose=AccessPurpose.SOS_TRANSMISSION, resource=None, remote_transmission=True)
    )
    assert result.decision is SafetyPrivacyDecision.ALLOW


def test_blocks_implicit_biometric_processing() -> None:
    result = evaluate_safety_privacy(
        request(resource=SensitiveResource.CAMERA, biometric_processing=True)
    )
    assert result.decision is SafetyPrivacyDecision.BLOCK


def test_requires_review_for_consequential_action() -> None:
    result = evaluate_safety_privacy(
        request(purpose=AccessPurpose.SOS_TRANSMISSION, resource=None, remote_transmission=True, consequential_action=True)
    )
    assert result.decision is SafetyPrivacyDecision.REVIEW


def test_requires_minimization_before_access_when_request_is_not_minimized() -> None:
    result = evaluate_safety_privacy(request(data_minimization=False))
    assert result.decision is SafetyPrivacyDecision.MINIMIZE


def test_blocks_identity_without_capability() -> None:
    denied = IdentityContext(
        principal=Principal(principal_id="test-principal", interface="test")
    )
    result = evaluate_safety_privacy(request(identity=denied))
    assert result.decision is SafetyPrivacyDecision.BLOCK


def test_consequential_review_preserves_execution_context() -> None:
    execution_context = CapabilityExecutionContext.for_capability(
        context := context(),
        capability_id="sos:trigger",
        action="sos:trigger",
        surface="test",
        resource_id="sos-1",
        idempotency_key="idem-sos-1",
        risk_level="high",
        side_effect_class=SideEffectClass.EXTERNAL_SIDE_EFFECT,
    )
    result = evaluate_safety_privacy(
        request(
            identity=context,
            capability="safety:privacy",
            purpose=AccessPurpose.SOS_TRANSMISSION,
            resource=None,
            remote_transmission=True,
            consequential_action=True,
            execution_context=execution_context,
        )
    )
    assert result.decision is SafetyPrivacyDecision.REVIEW
