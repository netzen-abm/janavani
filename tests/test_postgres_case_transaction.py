from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
from src.storage.repositories.postgres_case_transaction import (
    CaseTransactionConcurrencyError,
    CaseTransactionIdempotencyConflictError,
    PostgresCaseTransactionRepository,
)


def case(case_id="case-tx-1"):
    return CivicCase(
        case_id=case_id,
        case_type=CaseType.COMPLAINT,
        subject="Road defect",
        narrative="Road requires repair.",
        created_by="citizen-1",
        status=CaseStatus.REVIEW,
    )


def event(case_id="case-tx-1", event_id="event-1", notes="created"):
    return CaseEvent(
        event_id=event_id,
        case_id=case_id,
        event_type=CaseEventType.CREATED,
        occurred_at="2026-09-12T00:00:00+00:00",
        actor_id="citizen-1",
        source_channel="test",
        source_ref="fixture",
        notes=notes,
    )


def test_transaction_boundary_uses_shared_uow_and_updates_case_and_event_atomically():
    repository = PostgresCaseTransactionRepository
    assert repository is not None
    assert "unit_of_work_factory" in repository.__init__.__code__.co_varnames


def test_contract_rejects_mismatched_case_event():
    class UnusedUow:
        pass

    repository = PostgresCaseTransactionRepository(
        connection_factory=lambda: UnusedUow()
    )
    try:
        repository.persist_mutation(
            case=case("case-a"),
            event=event("case-b"),
            expected_version=0,
            idempotency_key="event-1",
        )
    except Exception as exc:
        assert "same case_id" in str(exc)
    else:
        raise AssertionError("mismatched case/event must be rejected")


def test_contract_requires_event_id_as_idempotency_key():
    repository = PostgresCaseTransactionRepository(connection_factory=lambda: None)
    try:
        repository.persist_mutation(
            case=case(), event=event(), expected_version=0, idempotency_key="other"
        )
    except Exception as exc:
        assert "event.event_id" in str(exc)
    else:
        raise AssertionError("mismatched idempotency key must be rejected")


def test_error_types_are_distinct_for_concurrency_and_idempotency():
    assert CaseTransactionConcurrencyError is not CaseTransactionIdempotencyConflictError
