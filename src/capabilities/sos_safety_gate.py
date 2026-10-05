"""SOS-specific adapter for the shared safety/privacy decision boundary."""
from __future__ import annotations

from src.capabilities.safety_privacy import AccessPurpose, SafetyPrivacyDecision, SafetyPrivacyRequest, SensitiveResource, evaluate_safety_privacy
from src.core.sos import SOSRequest
from src.core.execution import SideEffectClass
from src.identity.context import IdentityContext

CAPABILITY_ID = "sos:trigger"

class CanonicalSOSSafetyPrivacyGate:
    """Adapt the canonical Safety/Privacy boundary to SOS decisions."""
    def evaluate(self, request: SOSRequest, *, identity: IdentityContext):
        purpose = AccessPurpose.SOS_TRANSMISSION if request.remote_transmission else AccessPurpose.SOS
        return evaluate_safety_privacy(SafetyPrivacyRequest(
            identity=identity, purpose=purpose,
            resource=SensitiveResource.FILES if request.evidence_refs else None,
            capability=CAPABILITY_ID, explicit_user_choice=request.explicit_user_choice,
            remote_transmission=request.remote_transmission,
            consequential_action=request.consequential_action,
            execution_context=request.execution_context,
            explicit_user_approval=request.explicit_user_approval,
        )).decision
