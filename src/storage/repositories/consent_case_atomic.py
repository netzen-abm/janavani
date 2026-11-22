"""Atomic persistence boundary for explicit consent and Case audit state.

The capability layer owns identity authorization and consent semantics. This
adapter boundary owns one persistence invariant: a consent grant and its
Case reference/event commit together, with replay of the same citizen action
returning the original grant.
"""
from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Protocol

from src.core.consent import Consent
from src.core.civic_case import CaseEventType, CivicCase


class ConsentIdempotencyConflictError(RuntimeError):
    """One action key was reused with a different consent payload."""


class ConsentCaseAtomicRepository(Protocol):
    def save_consent_and_case(
        self,
        consent: Consent,
        case: CivicCase,
        *,
        principal_id: str,
        action_fingerprint: str | None = None,
    ) -> Consent:
        """Atomically persist consent + Case state and return the durable grant.

        When action_fingerprint is present, it identifies one explicit citizen
        action. Replaying that key with the same payload returns the original
        grant; reusing it with a different payload must fail closed.
        """
        ...


class InMemoryConsentCaseAtomicRepository:
    """Thread-safe transactional adapter for the in-memory test/dev providers.

    It snapshots both in-memory stores under one lock and restores them if
    either write fails. This adapter is deliberately limited to the existing
    in-memory repositories; it is not a substitute for durable DB transactions.
    """

    def __init__(self, *, consent_repository, case_repository) -> None:
        if not hasattr(consent_repository, "_items") or not hasattr(case_repository, "_cases"):
            raise TypeError("In-memory atomic consent requires the reference in-memory repositories")
        self._consents = consent_repository
        self._cases = case_repository
        self._lock = RLock()
        self._actions: dict[tuple[str, str], Consent] = {}

    @staticmethod
    def _same_payload(existing: Consent, incoming: Consent) -> bool:
        return (
            existing.consent_id == incoming.consent_id
            and existing.subject_id == incoming.subject_id
            and existing.purpose == incoming.purpose
            and existing.scope == incoming.scope
            and existing.grant_type is incoming.grant_type
            and existing.status is incoming.status
            and existing.expires_at == incoming.expires_at
            and existing.revoked_at == incoming.revoked_at
            and existing.proof_ref == incoming.proof_ref
        )

    @staticmethod
    def _verify_event(case: CivicCase, consent: Consent, principal_id: str) -> None:
        event_id = f"consent-{consent.consent_id}"
        event = next((item for item in case.events if item.event_id == event_id), None)
        if event is None:
            raise RuntimeError("Persisted consent is missing its Case audit event")
        if (
            event.case_id != case.case_id
            or event.event_type is not CaseEventType.CONSENT_RECORDED
            or event.actor_id != principal_id
            or event.notes != consent.purpose
            or event.source_ref != consent.proof_ref
            or consent.consent_id not in case.consent_refs
        ):
            raise RuntimeError("Persisted consent event does not match its grant")

    def save_consent_and_case(
        self, consent: Consent, case: CivicCase, *, principal_id: str,
        action_fingerprint: str | None = None,
    ) -> Consent:
        if not principal_id.strip():
            raise ValueError("principal_id is required")
        if consent.subject_id != principal_id or case.created_by != principal_id:
            raise PermissionError("Consent and Case must belong to the transaction principal")
        self._verify_event(case, consent, principal_id)

        with self._lock:
            action_key = (principal_id, action_fingerprint) if action_fingerprint else None
            mapped = self._actions.get(action_key) if action_key else None
            existing = mapped or self._consents.get(consent.consent_id, principal_id=principal_id)
            current_case = deepcopy(self._cases.get(case.case_id, principal_id=principal_id))
            if current_case is None or current_case.created_by != principal_id:
                raise LookupError("Case not found")
            stored_event = next(
                (event for event in current_case.events if event.event_id == f"consent-{consent.consent_id}"),
                None,
            )
            if existing is not None:
                if not self._same_payload(existing, consent):
                    if action_key and mapped is not None:
                        raise ConsentIdempotencyConflictError(
                            "Consent action key was reused with different content"
                        )
                    raise ValueError("Consent identifier already has different content")
                if stored_event is not None:
                    self._verify_event(current_case, existing, principal_id)
                    if action_key:
                        self._actions[action_key] = existing
                    return existing
                if action_key:
                    raise RuntimeError("Persisted consent action is missing its Case audit event")
            if case.version != current_case.version:
                raise RuntimeError(
                    f"Expected Case version {case.version}, found {current_case.version}"
                )

            consent_snapshot = deepcopy(self._consents._items)
            case_snapshot = deepcopy(self._cases._cases)
            try:
                if existing is None:
                    self._consents.save(consent, principal_id=principal_id)
                event = next(
                    item for item in case.events if item.event_id == f"consent-{consent.consent_id}"
                )
                case.version = current_case.version + 1
                case.updated_at = event.occurred_at
                self._cases.save(case, principal_id=principal_id)
            except Exception:
                self._consents._items.clear()
                self._consents._items.update(consent_snapshot)
                self._cases._cases.clear()
                self._cases._cases.update(case_snapshot)
                raise

            if action_key:
                self._actions[action_key] = existing or consent
            return existing or consent
