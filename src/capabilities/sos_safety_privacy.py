"""Composition adapter between canonical SOS and Safety/Privacy boundaries.

This module is intentionally an integration seam: the SOS capability remains
provider-neutral and does not import the concrete Safety/Privacy policy
implementation into its core orchestration layer.
"""
from __future__ import annotations

from src.capabilities.safety_privacy import (
    AccessPurpose,
    SafetyPrivacyDecision,
    SafetyPrivacyDecisionBoundary,
    SafetyPrivacyRequest,
)
from src.core.sos import SOSRequest
from src.identity.context import IdentityContext


class SOSSafetyPrivacyGate:
    """Translate an SOS request into the canonical Safety/Privacy policy model."""

    def __init__(self, boundary: SafetyPrivacyDecisionBoundary | None = None) -> None:
        self._boundary = boundary or SafetyPrivacyDecisionBoundary()

    def evaluate(self, request: SOSRequest, *, identity: IdentityContext) -> str:
        purpose = (
            AccessPurpose.SOS_TRANSMISSION
            if request.remote_transmission
            else AccessPurpose.SOS
        )
        result = self._boundary.evaluate(
            SafetyPrivacyRequest(
                identity=identity,
                purpose=purpose,
                explicit_user_choice=request.explicit_user_choice,
                remote_transmission=request.remote_transmission,
                consequential_action=request.consequential_action,
                data_minimization=True,
            )
        )
        return result.decision.value.upper()
