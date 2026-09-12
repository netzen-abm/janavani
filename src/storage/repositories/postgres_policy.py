"""Provider-neutral PostgreSQL adapter for composed authorization policy state."""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from src.access.policy_composition import DelegationGrant, ServiceIdentityPolicy
from src.core.consent import Consent, ConsentGrantType, ConsentStatus


class PostgresPolicyRepository:
    """Durable adapter implementing the provider-neutral PolicyRepository contract.

    Policy state is persisted through the canonical Consent storage boundary.
    This adapter does not evaluate authorization, activate RLS, or grant authority
    merely because a row exists.
    """

    def __init__(self, *, connection_factory: Callable[[], Any] | None = None, dsn: str | None = None) -> None:
        if connection_factory is None and not (dsn or os.getenv("JANAVANI_POSTGRES_DSN")):
            raise ValueError("PostgreSQL provider requires a DSN or connection factory")
        self._connection_factory = connection_factory
        self._dsn = dsn or os.getenv("JANAVANI_POSTGRES_DSN")

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    def save_delegation(self, delegation: DelegationGrant) -> None:
        if not delegation.delegation_id or not delegation.grantor_id or not delegation.delegate_id:
            raise ValueError("delegation identity fields must not be empty")
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO janavani_delegation_grants
                        (delegation_id, grantor_id, delegate_id, capabilities, actions,
                         resource_ids, expires_at, revoked)
                        VALUES (%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s)
                        ON CONFLICT (delegation_id) DO UPDATE SET
                        grantor_id=EXCLUDED.grantor_id, delegate_id=EXCLUDED.delegate_id,
                        capabilities=EXCLUDED.capabilities, actions=EXCLUDED.actions,
                        resource_ids=EXCLUDED.resource_ids, expires_at=EXCLUDED.expires_at,
                        revoked=EXCLUDED.revoked""", (
                        delegation.delegation_id, delegation.grantor_id, delegation.delegate_id,
                        json.dumps(sorted(delegation.capabilities)), json.dumps(sorted(delegation.actions)),
                        json.dumps(sorted(delegation.resource_ids)), delegation.expires_at, delegation.revoked,
                    ))

    def get_delegation(self, delegation_id: str) -> DelegationGrant | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT delegation_id, grantor_id, delegate_id, capabilities,
                    actions, resource_ids, expires_at, revoked FROM janavani_delegation_grants
                    WHERE delegation_id=%s""", (delegation_id,))
                row = cursor.fetchone()
        return self._hydrate_delegation(row) if row else None

    def list_delegations_for_delegate(self, delegate_id: str) -> tuple[DelegationGrant, ...]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT delegation_id, grantor_id, delegate_id, capabilities,
                    actions, resource_ids, expires_at, revoked FROM janavani_delegation_grants
                    WHERE delegate_id=%s ORDER BY delegation_id""", (delegate_id,))
                rows = cursor.fetchall()
        return tuple(self._hydrate_delegation(row) for row in rows)

    def save_consent(self, consent: Consent) -> None:
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO civic_case_consents
                        (consent_id, subject_id, purpose, scope, grant_type, status,
                         created_at, expires_at, revoked_at, proof_ref)
                        VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (consent_id) DO UPDATE SET subject_id=EXCLUDED.subject_id,
                        purpose=EXCLUDED.purpose, scope=EXCLUDED.scope,
                        grant_type=EXCLUDED.grant_type, status=EXCLUDED.status,
                        created_at=EXCLUDED.created_at, expires_at=EXCLUDED.expires_at,
                        revoked_at=EXCLUDED.revoked_at, proof_ref=EXCLUDED.proof_ref""", (
                        consent.consent_id, consent.subject_id, consent.purpose,
                        json.dumps(list(consent.scope)), consent.grant_type.value,
                        consent.status.value, consent.created_at, consent.expires_at,
                        consent.revoked_at, consent.proof_ref,
                    ))

    def get_consent(self, consent_id: str) -> Consent | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT consent_id, subject_id, purpose, scope, grant_type,
                    status, created_at, expires_at, revoked_at, proof_ref
                    FROM civic_case_consents WHERE consent_id=%s""", (consent_id,))
                row = cursor.fetchone()
        return self._hydrate_consent(row) if row else None

    def list_consents_for_subject(self, subject_id: str) -> tuple[Consent, ...]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT consent_id, subject_id, purpose, scope, grant_type,
                    status, created_at, expires_at, revoked_at, proof_ref
                    FROM civic_case_consents WHERE subject_id=%s
                    ORDER BY created_at, consent_id""", (subject_id,))
                rows = cursor.fetchall()
        return tuple(self._hydrate_consent(row) for row in rows)

    def save_service_policy(self, principal_id: str, policy: ServiceIdentityPolicy) -> None:
        if not principal_id:
            raise ValueError("principal_id must not be empty")
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO janavani_service_identity_policies
                        (principal_id, allowed_capabilities, allowed_actions)
                        VALUES (%s,%s::jsonb,%s::jsonb)
                        ON CONFLICT (principal_id) DO UPDATE SET
                        allowed_capabilities=EXCLUDED.allowed_capabilities,
                        allowed_actions=EXCLUDED.allowed_actions""", (
                        principal_id, json.dumps(sorted(policy.allowed_capabilities)),
                        json.dumps(sorted(policy.allowed_actions)),
                    ))

    def get_service_policy(self, principal_id: str) -> ServiceIdentityPolicy | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT allowed_capabilities, allowed_actions
                    FROM janavani_service_identity_policies WHERE principal_id=%s""", (principal_id,))
                row = cursor.fetchone()
        if not row:
            return None
        return ServiceIdentityPolicy(
            allowed_capabilities=frozenset(self._json_list(row[0])),
            allowed_actions=frozenset(self._json_list(row[1])),
        )

    @staticmethod
    def _json_list(value: Any) -> list[str]:
        if isinstance(value, str):
            value = json.loads(value)
        return list(value or [])

    @classmethod
    def _hydrate_delegation(cls, row: Any) -> DelegationGrant:
        return DelegationGrant(
            delegation_id=row[0], grantor_id=row[1], delegate_id=row[2],
            capabilities=frozenset(cls._json_list(row[3])), actions=frozenset(cls._json_list(row[4])),
            resource_ids=frozenset(cls._json_list(row[5])), expires_at=row[6], revoked=row[7],
        )

    @classmethod
    def _hydrate_consent(cls, row: Any) -> Consent:
        return Consent(
            consent_id=row[0], subject_id=row[1], purpose=row[2], scope=tuple(cls._json_list(row[3])),
            grant_type=ConsentGrantType(row[4]), status=ConsentStatus(row[5]), created_at=row[6],
            expires_at=row[7], revoked_at=row[8], proof_ref=row[9],
        )
