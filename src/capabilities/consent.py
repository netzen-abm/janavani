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
from src.core.civic_case import CaseEventType
from src.identity.context import IdentityContext
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.consent_case_atomic import ConsentCaseAtomicRepository

CAPABILITY_ID = "case:consent"
PURPOSE_SUBMISSION = "case_submission"
PURPOSE_DOCUMENT_PREPARATION = "document_preparation"


@dataclass(frozen=True)
class ConsentResult:
    """Canonical consent record plus the resulting owned Case projection."""

    consent: Consent
    case: CivicCaseResult


class ConsentCapability:
    """Shared boundary for explicit, purpose- and scope-bound consent."""

    def __init__(self, *, repository: ConsentRepository, case_capability: CivicCaseCapability, atomic_repository: ConsentCaseAtomicRepository | None = None) -> None:
        self._repository = repository
        self._cases = case_capability
        self._atomic_repository = atomic_repository

    @staticmethod
    def _authorize_case_consent(identity: IdentityContext, case_id: str, operation: str) -> None:
        for capability in (CAPABILITY_ID, "case:write"):
            decision = authorize(AuthorizationRequest(
                context=identity, capability=capability, action="case:consent", resource_id=case_id
            ))
            if decision is not AuthorizationDecision.ALLOW:
                raise PermissionError(f"Identity is not authorized to {operation}")

    def record_submission_consent(self, case_id: str, *, scope: str, identity: IdentityContext, proof_ref: str | None = None) -> ConsentResult:
        """Persist consent for an actual Janavani external-delivery operation."""
        return self._record_consent(case_id, scope=scope, identity=identity, purpose=PURPOSE_SUBMISSION, proof_ref=proof_ref)

    def record_document_preparation_consent(self, case_id: str, *, scope: str, identity: IdentityContext, proof_ref: str | None = None) -> ConsentResult:
        """Persist consent for preparing a document the citizen will download and send."""
        return self._record_consent(case_id, scope=scope, identity=identity, purpose=PURPOSE_DOCUMENT_PREPARATION, proof_ref=proof_ref)

    def attach_existing_consent(self, case_id: str, consent_id: str, *, identity: IdentityContext) -> ConsentResult:
        """Attach only a persisted, active, principal-owned grant for this exact Case."""
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        self._authorize_case_consent(identity, case_id, "attach consent")
        consent = self._repository.get(consent_id, principal_id=identity.principal.principal_id)
        if consent is None or consent.subject_id != identity.principal.principal_id:
            raise LookupError("Consent grant not found")
        if consent.grant_type is not ConsentGrantType.EXPLICIT or not consent.is_authorized:
            raise PermissionError("Consent grant is not active and explicit")
        if not any(
            self._consent_id(case_id, consent.purpose, scope) == consent.consent_id
            for scope in consent.scope
        ):
            raise LookupError("Consent grant not found")

        event_id = f"consent-{consent.consent_id}"
        existing_event = next(
            (event for event in case.events if event.event_id == event_id),
            None,
        )
        if existing_event is not None:
            if (
                existing_event.event_type is not CaseEventType.CONSENT_RECORDED
                or existing_event.actor_id != identity.principal.principal_id
                or existing_event.notes != consent.purpose
                or existing_event.source_ref != consent.proof_ref
                or consent.consent_id not in case.consent_refs
            ):
                raise RuntimeError("Existing consent event does not match its persisted grant")
            return ConsentResult(
                consent=consent,
                case=CivicCaseResult(case, AuthorizationDecision.ALLOW),
            )

        if self._atomic_repository is not None:
            if consent.consent_id not in case.consent_refs:
                case.consent_refs.append(consent.consent_id)
            self._atomic_repository.save_consent_and_case(
                consent, case, principal_id=identity.principal.principal_id
            )
            attached = CivicCaseResult(case, AuthorizationDecision.ALLOW)
        else:
            attached = self._cases.add_consent(
                case_id,
                consent.consent_id,
                identity=identity,
                purpose=consent.purpose,
                proof_ref=consent.proof_ref,
                occurred_at=consent.created_at,
            )
        return ConsentResult(consent=consent, case=attached)

    def _record_consent(self, case_id: str, *, scope: str, identity: IdentityContext, purpose: str, proof_ref: str | None = None) -> ConsentResult:
        """Persist consent and attach its reference without advancing Case lifecycle."""
        if not scope.strip():
            raise ValueError("Consent scope is required")
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        self._authorize_case_consent(identity, case_id, "record consent")
        consent_id = self._consent_id(case_id, purpose, scope)
        consent = self._repository.get(consent_id, principal_id=identity.principal.principal_id)
        if consent is None:
            now = datetime.now(timezone.utc).isoformat()
            consent = Consent(
                consent_id=consent_id, subject_id=identity.principal.principal_id,
                purpose=purpose, scope=(scope,), grant_type=ConsentGrantType.EXPLICIT,
                status=ConsentStatus.GRANTED, created_at=now, proof_ref=proof_ref,
            )
            if self._atomic_repository is None:
                self._repository.save(consent, principal_id=identity.principal.principal_id)
        elif consent.subject_id != identity.principal.principal_id or not consent.authorizes(purpose, scope):
            raise PermissionError("Existing consent does not authorize this identity and scope")
        event_id = f"consent-{consent.consent_id}"
        existing_event = next(
            (event for event in case.events if event.event_id == event_id),
            None,
        )
        if existing_event is not None:
            if (
                existing_event.event_type is not CaseEventType.CONSENT_RECORDED
                or existing_event.actor_id != identity.principal.principal_id
                or existing_event.notes != purpose
                or existing_event.source_ref != consent.proof_ref
                or consent.consent_id not in case.consent_refs
            ):
                raise RuntimeError("Existing consent event does not match its persisted grant")
            return ConsentResult(
                consent=consent,
                case=CivicCaseResult(case, AuthorizationDecision.ALLOW),
            )
        if self._atomic_repository is not None:
            case.consent_refs.append(consent.consent_id)
            self._atomic_repository.save_consent_and_case(
                consent,
                case,
                principal_id=identity.principal.principal_id,
            )
            return ConsentResult(
                consent=consent,
                case=CivicCaseResult(case, AuthorizationDecision.ALLOW),
            )
        attached = self._cases.add_consent(
            case_id,
            consent.consent_id,
            identity=identity,
            purpose=purpose,
            proof_ref=consent.proof_ref,
            occurred_at=consent.created_at,
        )
        return ConsentResult(consent=consent, case=attached)

    @staticmethod
    def _consent_id(case_id: str, purpose: str, scope: str) -> str:
        digest = sha256(f"{case_id}:{purpose}:{scope}".encode()).hexdigest()[:32]
        return f"consent-{digest}"
