"""Canonical Safety/Privacy Decision Boundary.

This boundary evaluates purpose-bound access to sensitive device/data capabilities.
It deliberately does not grant OS permissions, upload data, or authorize external
consequential actions. Those remain separate concerns.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.access.consequential import (
    ConsequentialDecision,
    ConsequentialOperationRequest,
    gate_consequential_operation,
)
from src.core.execution import CapabilityExecutionContext
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
    SOS_TRANSMISSION = "sos_transmission"
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
    """Purpose-bound request for a sensitive resource or SOS operation."""

    identity: IdentityContext
    purpose: AccessPurpose
    resource: SensitiveResource | None = None
    capability: str = CAPABILITY_ID
    data_minimization: bool = True
    explicit_user_choice: bool = True
    background_access: bool = False
    continuous_access: bool = False
    remote_transmission: bool = False
    biometric_processing: bool = False
    consequential_action: bool = False
    execution_context: CapabilityExecutionContext | None = None
    explicit_user_approval: bool = False


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
        if request.remote_transmission and request.purpose not in {
            AccessPurpose.EXPLICIT_UPLOAD,
            AccessPurpose.SOS_TRANSMISSION,
        }:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Remote transmission requires an explicit upload or SOS-transmission purpose")
        if request.biometric_processing and request.resource is not SensitiveResource.BIOMETRIC_PROCESSING:
            return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Biometric processing must be separately scoped")

        resource_action = request.resource.value if request.resource is not None else "operation"
        authorization_request = AuthorizationRequest(
            context=request.identity,
            capability=request.capability,
            action=f"{request.purpose.value}:{resource_action}",
            risk_level="high" if request.consequential_action else "normal",
            requires_approval=request.consequential_action,
            execution_context=request.execution_context,
        )

        if request.consequential_action:
            if request.execution_context is None:
                return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Consequential action requires an execution context")
            decision = gate_consequential_operation(
                ConsequentialOperationRequest(
                    authorization=authorization_request,
                    execution_context=request.execution_context,
                    explicit_user_approval=request.explicit_user_approval,
                )
            )
            if decision is ConsequentialDecision.DENY:
                return SafetyPrivacyResult(SafetyPrivacyDecision.BLOCK, "Identity is not authorized for this consequential capability")
            if decision is ConsequentialDecision.CONSENT_REQUIRED:
                return SafetyPrivacyResult(SafetyPrivacyDecision.REVIEW, "Required consent is not satisfied")
            if decision is ConsequentialDecision.REQUIRE_APPROVAL:
                return SafetyPrivacyResult(SafetyPrivacyDecision.REVIEW, "Additional approval is required")
        else:
            decision = authorize(authorization_request)
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
