from __future__ import annotations

from src.access.policy_composition import DelegationGrant, ServiceIdentityPolicy
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.storage.repositories.postgres_policy import PostgresPolicyRepository


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.rows = []

    def __enter__(self): return self
    def __exit__(self, *_): return False

    def execute(self, sql, params=()):
        upper = sql.upper()
        if "JANAVANI_DELEGATION_GRANTS" in upper and "WHERE DELEGATE_ID" in upper:
            self.rows = [v for v in self.db.delegations.values() if v[2] == params[0]]
        elif "JANAVANI_DELEGATION_GRANTS" in upper and "WHERE DELEGATION_ID" in upper:
            value = self.db.delegations.get(params[0])
            self.rows = [value] if value else []
        elif "INSERT INTO JANAVANI_DELEGATION_GRANTS" in upper:
            self.db.delegations[params[0]] = tuple(params)
        elif "JANAVANI_POLICY_CONSENTS" in upper and "WHERE SUBJECT_ID" in upper:
            self.rows = [v for v in self.db.consents.values() if v[1] == params[0]]
        elif "JANAVANI_POLICY_CONSENTS" in upper and "WHERE CONSENT_ID" in upper:
            value = self.db.consents.get(params[0])
            self.rows = [value] if value else []
        elif "INSERT INTO JANAVANI_POLICY_CONSENTS" in upper:
            self.db.consents[params[0]] = tuple(params)
        elif "INSERT INTO JANAVANI_SERVICE_IDENTITY_POLICIES" in upper:
            self.db.services[params[0]] = tuple(params[1:])
        elif "JANAVANI_SERVICE_IDENTITY_POLICIES" in upper:
            value = self.db.services.get(params[0])
            self.rows = [value] if value else []

    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return list(self.rows)


class FakeTransaction:
    def __enter__(self): return self
    def __exit__(self, *_): return False


class FakeConnection:
    def __init__(self, db): self.db = db
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def transaction(self): return FakeTransaction()
    def cursor(self): return FakeCursor(self.db)


class FakeDb:
    def __init__(self):
        self.delegations = {}
        self.consents = {}
        self.services = {}


def delegation():
    return DelegationGrant(
        delegation_id="d-1", grantor_id="owner", delegate_id="delegate",
        capabilities=frozenset({"case:submit"}), actions=frozenset({"submit"}),
        resource_ids=frozenset({"case-1"}), expires_at="2099-01-01T00:00:00+00:00",
    )


def consent():
    return Consent(
        consent_id="c-1", subject_id="owner", purpose="civic_submission",
        scope=("case:submit",), grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED, created_at="2026-09-12T00:00:00+00:00",
    )


def test_policy_repository_round_trips_all_policy_families():
    db = FakeDb()
    repo = PostgresPolicyRepository(connection_factory=lambda: FakeConnection(db))

    d = delegation()
    c = consent()
    service = ServiceIdentityPolicy(
        allowed_capabilities=frozenset({"case:read"}), allowed_actions=frozenset({"read"})
    )
    repo.save_delegation(d)
    repo.save_consent(c)
    repo.save_service_policy("service-a", service)

    assert repo.get_delegation("d-1") == d
    assert repo.list_delegations_for_delegate("delegate") == (d,)
    assert repo.list_delegations_for_delegate("other") == ()
    assert repo.get_consent("c-1") == c
    assert repo.list_consents_for_subject("owner") == (c,)
    assert repo.list_consents_for_subject("other") == ()
    assert repo.get_service_policy("service-a") == service
    assert repo.get_service_policy("service-b") is None


def test_revoked_delegation_remains_durable_state():
    db = FakeDb()
    repo = PostgresPolicyRepository(connection_factory=lambda: FakeConnection(db))
    revoked = DelegationGrant(
        delegation_id="revoked", grantor_id="owner", delegate_id="delegate",
        capabilities=frozenset({"case:submit"}), revoked=True,
    )
    repo.save_delegation(revoked)
    assert repo.get_delegation("revoked") == revoked
    assert repo.get_delegation("revoked").revoked is True
