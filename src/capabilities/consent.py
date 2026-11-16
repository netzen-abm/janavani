"""Canonical consent capability for recording explicit user permission.

Access surfaces must use this boundary rather than persisting Consent objects or
mutating CivicCase consent references directly.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

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
            self._matches_consent_id(consent.consent_id, case_id, consent.purpose, scope)
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
            attached = self._cases._record_verified_consent(
                case_id, consent, identity=identity
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
        base_consent_id = self._consent_id(case_id, purpose, scope)
        prior_grants = [
            item
            for item in self._repository.list_for_subject(
                identity.principal.principal_id,
                principal_id=identity.principal.principal_id,
            )
            if item.subject_id == identity.principal.principal_id
            and item.purpose == purpose
            and scope in item.scope
            and self._matches_consent_id(item.consent_id, case_id, purpose, scope)
        ]
        active_grant = max(
            (
                item for item in prior_grants
                if item.grant_type is ConsentGrantType.EXPLICIT
                and item.authorizes(purpose, scope)
            ),
            key=lambda item: (item.created_at, item.consent_id),
            default=None,
        )
        if active_grant is not None:
            consent = active_grant
        else:
            # Preserve expired, denied and revoked grants as immutable history.
            # A fresh explicit citizen action creates a distinct grant version.
            consent_id = (
                base_consent_id
                if not prior_grants
                else f"{base_consent_id}:v:{uuid4().hex}"
            )
            consent = Consent(
                consent_id=consent_id,
                subject_id=identity.principal.principal_id,
                purpose=purpose,
                scope=(scope,),
                grant_type=ConsentGrantType.EXPLICIT,
                status=ConsentStatus.GRANTED,
                created_at=datetime.now(timezone.utc).isoformat(),
                proof_ref=proof_ref,
            )
            if self._atomic_repository is None:
                self._repository.save(
                    consent, principal_id=identity.principal.principal_id
                )
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
        attached = self._cases._record_verified_consent(
            case_id, consent, identity=identity
        )
        return ConsentResult(consent=consent, case=attached)

    @classmethod
    def _matches_consent_id(
        cls, consent_id: str, case_id: str, purpose: str, scope: str
    ) -> bool:
        base = cls._consent_id(case_id, purpose, scope)
        if consent_id == base:
            return True
        prefix = f"{base}:v:"
        version = consent_id[len(prefix):] if consent_id.startswith(prefix) else ""
        return len(version) == 32 and all(
            character in "0123456789abcdef" for character in version
        )

    @staticmethod
    def _consent_id(case_id: str, purpose: str, scope: str) -> str:
        digest = sha256(f"{case_id}:{purpose}:{scope}".encode()).hexdigest()[:32]
        return f"consent-{digest}"
