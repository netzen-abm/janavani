"""Canonical consent capability for recording explicit user permission.

Access surfaces must use this boundary rather than persisting Consent objects or
mutating CivicCase consent references directly.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.identity.context import IdentityContext
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.storage.repositories.consent import ConsentRepository

CAPABILITY_ID = "case:consent"
PURPOSE_SUBMISSION = "case_submission"


@dataclass(frozen=True)
class ConsentResult:
    """Canonical consent record plus the resulting owned Case projection."""

    consent: Consent
    case: CivicCaseResult


class ConsentCapability:
    """Shared boundary for explicit, purpose- and scope-bound consent."""

    def __init__(self, *, repository: ConsentRepository, case_capability: CivicCaseCapability) -> None:
        self._repository = repository
        self._cases = case_capability

    def record_submission_consent(self, case_id: str, *, scope: str, identity: IdentityContext, proof_ref: str | None = None) -> ConsentResult:
        """Persist explicit submission consent and attach it to the owned Case."""
        if not scope.strip():
            raise ValueError("Consent scope is required")
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        decision = authorize(AuthorizationRequest(
            context=identity, capability=CAPABILITY_ID, action="case:consent", resource_id=case_id
        ))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to record consent")
        consent_id = self._consent_id(case_id, PURPOSE_SUBMISSION, scope)
        consent = self._repository.get(consent_id, principal_id=identity.principal.principal_id)
        if consent is None:
            now = datetime.now(timezone.utc).isoformat()
            consent = Consent(
                consent_id=consent_id, subject_id=identity.principal.principal_id,
                purpose=PURPOSE_SUBMISSION, scope=(scope,), grant_type=ConsentGrantType.EXPLICIT,
                status=ConsentStatus.GRANTED, created_at=now, proof_ref=proof_ref,
            )
            self._repository.save(consent, principal_id=identity.principal.principal_id)
        elif consent.subject_id != identity.principal.principal_id or not consent.authorizes(PURPOSE_SUBMISSION, scope):
            raise PermissionError("Existing consent does not authorize this identity and scope")
        attached = self._cases.add_consent(case_id, consent.consent_id, identity=identity)
        if attached.case.status.value == "draft":
            attached = self._cases.start_review(case_id, identity=identity)
        if attached.case.status.value == "review":
            attached = self._cases.approve(case_id, identity=identity)
        return ConsentResult(consent=consent, case=attached)

    @staticmethod
    def _consent_id(case_id: str, purpose: str, scope: str) -> str:
        digest = sha256(f"{case_id}:{purpose}:{scope}".encode()).hexdigest()[:32]
        return f"consent-{digest}"
