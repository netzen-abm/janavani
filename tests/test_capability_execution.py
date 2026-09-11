from src.core.execution import (
    CapabilityExecutionContext,
    ProvenanceRecord,
    SideEffectClass,
    TrustClass,
)
from src.core.operation import OperationRecord, OperationState
from src.identity.context import anonymous_context
from src.storage.repositories.operation import InMemoryOperationRepository


def test_context_inherits_request_correlation_id() -> None:
    identity = anonymous_context("citizen-1", request_id="req-1")
    context = CapabilityExecutionContext.for_capability(
        identity,
        capability_id="case:create",
        action="create",
        surface="web",
    )
    assert context.correlation_id == "req-1"
    assert context.operation_id.startswith("op_")


def test_external_side_effect_requires_idempotency() -> None:
    identity = anonymous_context("citizen-1")
    try:
        CapabilityExecutionContext.for_capability(
            identity,
            capability_id="case:submit",
            action="submit",
            surface="telegram",
            side_effect_class=SideEffectClass.EXTERNAL_SIDE_EFFECT,
        )
    except ValueError as exc:
        assert "idempotency_key" in str(exc)
    else:
        raise AssertionError("external side effect without idempotency must fail")


def test_provenance_validates_confidence() -> None:
    try:
        ProvenanceRecord("source-1", TrustClass.AI_GENERATED, confidence=1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid confidence must fail")


def test_operation_repository_prevents_idempotency_collision() -> None:
    repo = InMemoryOperationRepository()
    first = OperationRecord("op-1", "case:submit", "submit", OperationState.REQUESTED, "citizen-1", idempotency_key="idem-1")
    second = OperationRecord("op-2", "case:submit", "submit", OperationState.REQUESTED, "citizen-1", idempotency_key="idem-1")
    repo.save(first)
    try:
        repo.save(second)
    except ValueError as exc:
        assert "Idempotency" in str(exc)
    else:
        raise AssertionError("idempotency collision must fail")


def test_failed_operation_requires_error_code() -> None:
    try:
        OperationRecord("op-1", "case:create", "create", OperationState.FAILED, "citizen-1")
    except ValueError:
        pass
    else:
        raise AssertionError("failed operation without error code must fail")
