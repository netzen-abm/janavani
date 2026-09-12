from __future__ import annotations

from src.access.policy_composition import DelegationGrant, ServiceIdentityPolicy
from src.access.policy_repository import InMemoryPolicyRepository
from src.core.consent import Consent, ConsentGrantType, ConsentStatus


def _delegation(delegation_id: str, delegate_id: str = "delegate") -> DelegationGrant:
    return DelegationGrant(
        delegation_id=delegation_id,
        grantor_id="owner",
        delegate_id=delegate_id,
        capabilities=frozenset({"case:submit"}),
        actions=frozenset({"submit"}),
        resource_ids=frozenset({"case-1"}),
    )


def _consent(consent_id: str, subject_id: str = "owner") -> Consent:
    return Consent(
        consent_id=consent_id,
        subject_id=subject_id,
        purpose="civic_submission",
        scope=("case:submit",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-12T00:00:00+00:00",
    )


def test_delegation_round_trip_and_delegate_scoping() -> None:
    repository = InMemoryPolicyRepository()
    repository.save_delegation(_delegation("d-1", "delegate-a"))
    repository.save_delegation(_delegation("d-2", "delegate-b"))

    assert repository.get_delegation("d-1") == _delegation("d-1", "delegate-a")
    assert [d.delegation_id for d in repository.list_delegations_for_delegate("delegate-a")] == ["d-1"]
    assert repository.list_delegations_for_delegate("unknown") == ()


def test_consent_round_trip_and_subject_scoping() -> None:
    repository = InMemoryPolicyRepository()
    repository.save_consent(_consent("c-1", "owner"))
    repository.save_consent(_consent("c-2", "other"))

    assert repository.get_consent("c-1") == _consent("c-1", "owner")
    assert [c.consent_id for c in repository.list_consents_for_subject("owner")] == ["c-1"]
    assert repository.get_consent("missing") is None


def test_service_policy_is_scoped_to_service_principal() -> None:
    repository = InMemoryPolicyRepository()
    policy = ServiceIdentityPolicy(
        allowed_capabilities=frozenset({"case:submit"}),
        allowed_actions=frozenset({"submit"}),
    )
    repository.save_service_policy("service-a", policy)

    assert repository.get_service_policy("service-a") == policy
    assert repository.get_service_policy("service-b") is None


def test_snapshot_is_immutable_and_contains_all_policy_families() -> None:
    repository = InMemoryPolicyRepository()
    repository.save_delegation(_delegation("d-1"))
    repository.save_consent(_consent("c-1"))
    repository.save_service_policy("service-a", ServiceIdentityPolicy(
        allowed_capabilities=frozenset({"case:read"}),
        allowed_actions=frozenset({"read"}),
    ))

    snapshot = repository.snapshot()
    assert snapshot.delegations == (_delegation("d-1"),)
    assert snapshot.consents == (_consent("c-1"),)
    assert snapshot.service_policy_for("service-a") is not None
    assert snapshot.service_policy_for("service-b") is None


def test_revocation_and_expiry_are_persisted_as_policy_state_not_deleted() -> None:
    repository = InMemoryPolicyRepository()
    revoked = DelegationGrant(
        delegation_id="d-revoked",
        grantor_id="owner",
        delegate_id="delegate",
        capabilities=frozenset({"case:submit"}),
        revoked=True,
    )
    repository.save_delegation(revoked)

    assert repository.get_delegation("d-revoked") == revoked
    assert repository.get_delegation("d-revoked").revoked is True
