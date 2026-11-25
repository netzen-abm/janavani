"""Canonical consent capability for recording explicit user permission.

Every explicit confirmation carries a stable action_id. Re-delivery of the same
action is idempotent; a later, separately confirmed action creates a new
historical grant. Consent and its Case audit event use one atomic repository.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.identity.context import IdentityContext
from src.storage.repositories.consent import ConsentRepository, InMemoryConsentRepository
from src.storage.repositories.consent_case_atomic import (
    ConsentCaseAtomicRepository,
    InMemoryConsentCaseAtomicRepository,
)

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

    def __init__(
        self,
        *,
        repository: ConsentRepository,
        case_capability: CivicCaseCapability,
        atomic_repository: ConsentCaseAtomicRepository | None = None,
    ) -> None:
        self._repository = repository
        self._cases = case_capability
        if (
            atomic_repository is None
            and isinstance(repository, InMemoryConsentRepository)
            and hasattr(case_capability.repository, "_cases")
        ):
            atomic_repository = InMemoryConsentCaseAtomicRepository(
                consent_repository=repository,
                case_repository=case_capability.repository,
            )
        self._atomic_repository = atomic_repository

    @staticmethod
    def _authorize_case_consent(identity: IdentityContext, case_id: str, operation: str) -> None:
        for capability in (CAPABILITY_ID, "case:write"):
            decision = authorize(AuthorizationRequest(
                context=identity, capability=capability, action="case:consent", resource_id=case_id
            ))
            if decision is not AuthorizationDecision.ALLOW:
                raise PermissionError(f"Identity is not authorized to {operation}")

    def record_submission_consent(
        self,
        case_id: str,
        *,
        scope: str,
        identity: IdentityContext,
        action_id: str,
        proof_ref: str | None = None,
    ) -> ConsentResult:
        """Persist consent for an actual Janavani external-delivery operation."""
        return self._record_consent(
            case_id, scope=scope, identity=identity, action_id=action_id,
            purpose=PURPOSE_SUBMISSION, proof_ref=proof_ref,
        )

    def record_document_preparation_consent(
        self,
        case_id: str,
        *,
        scope: str,
        identity: IdentityContext,
        action_id: str,
        proof_ref: str | None = None,
    ) -> ConsentResult:
        """Persist consent for preparing a document the citizen will download and send."""
        return self._record_consent(
            case_id, scope=scope, identity=identity, action_id=action_id,
            purpose=PURPOSE_DOCUMENT_PREPARATION, proof_ref=proof_ref,
        )

    def attach_existing_consent(
        self, case_id: str, consent_id: str, *, identity: IdentityContext
    ) -> ConsentResult:
        """Attach only a persisted, active, principal-owned grant for this exact Case."""
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        self._authorize_case_consent(identity, case_id, "attach consent")
        consent = self._repository.get(
            consent_id, principal_id=identity.principal.principal_id
        )
        if consent is None or consent.subject_id != identity.principal.principal_id:
            raise LookupError("Consent grant not found")
        if consent.grant_type is not ConsentGrantType.EXPLICIT or not consent.is_authorized:
            raise PermissionError("Consent grant is not active and explicit")
        if not any(
            self._matches_consent_id(consent.consent_id, case_id, consent.purpose, scope)
            for scope in consent.scope
        ):
            raise LookupError("Consent grant not found")

        if self._atomic_repository is None:
            raise RuntimeError("Atomic consent persistence is required; no Case mutation was attempted")
        case_for_write = self._cases._apply_verified_consent(
            deepcopy(case), consent, identity=identity
        )
        persisted = self._atomic_repository.save_consent_and_case(
            consent, case_for_write, principal_id=identity.principal.principal_id
        )
        refreshed = self._cases.get_owned(case_id, identity=identity)
        if refreshed is None:
            raise RuntimeError("Case disappeared after atomic consent attachment")
        return ConsentResult(persisted, CivicCaseResult(refreshed, AuthorizationDecision.ALLOW))

    def require_active_document_preparation_consent(
        self, case_id: str, *, identity: IdentityContext
    ) -> Consent:
        """Require an active, explicit, principal- and Case-bound preparation grant."""
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        self._authorize_case_consent(identity, case_id, "approve document preparation")
        principal_id = identity.principal.principal_id
        for consent_id in case.consent_refs:
            consent = self._repository.get(consent_id, principal_id=principal_id)
            if (
                consent is None
                or consent.subject_id != principal_id
                or consent.grant_type is not ConsentGrantType.EXPLICIT
            ):
                continue
            if any(
                consent.authorizes(PURPOSE_DOCUMENT_PREPARATION, scope)
                and self._matches_consent_id(
                    consent.consent_id, case_id, PURPOSE_DOCUMENT_PREPARATION, scope
                )
                for scope in consent.scope
            ):
                return consent
        raise PermissionError(
            "Active explicit document-preparation consent bound to this Case is required"
        )

    def _record_consent(
        self,
        case_id: str,
        *,
        scope: str,
        identity: IdentityContext,
        action_id: str,
        purpose: str,
        proof_ref: str | None = None,
    ) -> ConsentResult:
        """Persist one explicit action; a stable action key makes retries idempotent."""
        if not scope.strip():
            raise ValueError("Consent scope is required")
        normalized_action_id = action_id.strip()
        if not normalized_action_id or len(normalized_action_id) > 200:
            raise ValueError("A stable consent action_id between 1 and 200 characters is required")
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        self._authorize_case_consent(identity, case_id, "record consent")
        if self._atomic_repository is None:
            raise RuntimeError("Atomic consent persistence is required; no grant was written")

        action_fingerprint = sha256(normalized_action_id.encode("utf-8")).hexdigest()
        consent_id = (
            f"{self._consent_id(case_id, purpose, scope)}:a:{action_fingerprint[:32]}"
        )
        consent = Consent(
            consent_id=consent_id,
            subject_id=identity.principal.principal_id,
            purpose=purpose,
            scope=(scope,),
            grant_type=ConsentGrantType.EXPLICIT,
            status=ConsentStatus.GRANTED,
            created_at=datetime.now(UTC).isoformat(),
            proof_ref=proof_ref,
        )
        case_for_write = self._cases._apply_verified_consent(
            deepcopy(case), consent, identity=identity
        )
        persisted = self._atomic_repository.save_consent_and_case(
            consent, case_for_write, principal_id=identity.principal.principal_id,
            action_fingerprint=action_fingerprint,
        )
        refreshed = self._cases.get_owned(case_id, identity=identity)
        if refreshed is None:
            raise RuntimeError("Case disappeared after atomic consent recording")
        return ConsentResult(persisted, CivicCaseResult(refreshed, AuthorizationDecision.ALLOW))

    @classmethod
    def _matches_consent_id(
        cls, consent_id: str, case_id: str, purpose: str, scope: str
    ) -> bool:
        base = cls._consent_id(case_id, purpose, scope)
        if consent_id == base:
            return True
        for marker, length in ((":v:", 32), (":a:", 32)):
            prefix = f"{base}{marker}"
            version = consent_id[len(prefix):] if consent_id.startswith(prefix) else ""
            if len(version) == length and all(
                character in "0123456789abcdef" for character in version
            ):
                return True
        return False

    @staticmethod
    def _consent_id(case_id: str, purpose: str, scope: str) -> str:
        digest = sha256(f"{case_id}:{purpose}:{scope}".encode()).hexdigest()[:32]
        return f"consent-{digest}"
