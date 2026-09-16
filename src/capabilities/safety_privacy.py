"""Canonical Safety/Privacy Decision Boundary.

This boundary evaluates purpose-bound access to sensitive device/data capabilities.
It deliberately does not grant OS permissions, upload data, or authorize external
consequential actions. Those remain separate concerns.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.identity.context import IdentityContext

CAPABILITY_ID = "safety:privacy"


class SafetyPrivacyDecision(str, Enum):
    ALLOW = "allow"
    MINIMIZE = "minimize"
    BLOCK = "block"
    REVIEW = "review"


class AccessPurpose(str, Enum):
    EVIDENCE_CAPTURE = "evidence_capture"
    SOS = "sos"
    LOCAL_ANALYSIS = "local_analysis"
    EXPLICIT_UPLOAD = "explicit_upload"
    EXTERNAL_ACTION = "external_action"


class SensitiveResource(str, Enum):
    CAMERA = "camera"
    MICROPHONE = "microphone"
    LOCATION = "location"
    CONTACTS = "contacts"
    FILES = "files"
    SENSORS = "sensors"
    BIOMETRIC_PROCESSING = "biometric_processing"


@dataclass(frozen=True)
class SafetyPrivacyRequest:
    """Purpose-bound request for a sensitive resource."""

    identity: IdentityContext
    purpose: AccessPurpose
    resource: SensitiveResource
    capability: str = CAPABILITY_ID
    data_minimization: bool = True
    explicit_user_choice: bool = True
    background_access: bool = False
    continuous_access: bool = False
    remote_transmission: bool = False
    biometric_processing: bool = False
    consequential_action: bool = False


@dataclass(frozen=True)
class SafetyPrivacyResult:
    decision: SafetyPrivacyDecision
    reason: str


class SafetyPrivacyDecisionBoundary:
    """Deterministic policy boundary for safety-sensitive data access."""

    def evaluate(self, request: SafetyPrivacyRequest) -> SafetyPrivacyResult:
        if not request.explicit_user_choice:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Explicit user choice is required")
        if request.background_access or request.continuous_access:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Background or continuous sensitive access is not permitted by this boundary")
        if request.remote_transmission and request.purpose is not AccessPurpose.EXPLICIT_UPLOAD:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Remote transmission requires an explicit upload purpose")
        if request.biometric_processing and request.resource is not SensitiveResource.BIOMETRIC_PROCESSING:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Biometric processing must be separately scoped")
        if request.consequential_action and request.purpose is not AccessPurpose.EXTERNAL_ACTION:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Consequential action requires the external-action boundary")

        decision = authorize(AuthorizationRequest(
            context=request.identity,
            capability=request.capability,
            action=f"{request.purpose.value}:{request.resource.value}",
            risk_level="high" if request.consequential_action else "normal",
            requires_approval=request.consequential_action,
        ))
        if decision is AuthorizationDecision.DENY:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Identity is not authorized for this capability")
        if decision is AuthorizationDecision.REQUIRE_APPROVAL:
            return SafetyPrivacyResult(SafetyPrivacyDecision.REVIEW, "Additional approval is required")

        if not request.data_minimization:
            return SafetyPrivacyResult(SafetyPrivacyDecision.MINIMIZE, "Access is permitted only after data minimization")
        return SafetyPrivacyResult(SafetyPrivacyDecision.ALLOW, "Purpose-bound access permitted")


def evaluate_safety_privacy(request: SafetyPrivacyRequest) -> SafetyPrivacyResult:
    """Evaluate one request through the canonical shared boundary."""
    return SafetyPrivacyDecisionBoundary().evaluate(request)
