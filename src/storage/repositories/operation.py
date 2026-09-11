"""Provider-neutral persistence contract for capability operations."""
from __future__ import annotations

from typing import Protocol

from src.core.operation import OperationRecord


class OperationRepository(Protocol):
    def save(self, operation: OperationRecord) -> None:
        ...

    def get(self, operation_id: str) -> OperationRecord | None:
        ...

    def get_by_idempotency_key(self, idempotency_key: str) -> OperationRecord | None:
        ...


class InMemoryOperationRepository(OperationRepository):
    def __init__(self) -> None:
        self._items: dict[str, OperationRecord] = {}
        self._idempotency: dict[str, str] = {}

    def save(self, operation: OperationRecord) -> None:
        existing = self._items.get(operation.operation_id)
        if existing and existing != operation:
            raise ValueError("Operation records are immutable by operation_id")
        if operation.idempotency_key:
            owner = self._idempotency.get(operation.idempotency_key)
            if owner and owner != operation.operation_id:
                raise ValueError("Idempotency key is already bound to another operation")
            self._idempotency[operation.idempotency_key] = operation.operation_id
        self._items[operation.operation_id] = operation

    def get(self, operation_id: str) -> OperationRecord | None:
        return self._items.get(operation_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> OperationRecord | None:
        operation_id = self._idempotency.get(idempotency_key)
        return self._items.get(operation_id) if operation_id else None
