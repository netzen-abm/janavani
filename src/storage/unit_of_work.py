"""Provider-neutral Unit-of-Work boundary for atomic civic persistence."""
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol, Self


class UnitOfWork(AbstractContextManager, Protocol):
    """Transaction boundary shared by storage providers.

    A Unit of Work owns one provider resource and its transaction lifecycle.
    Coordinated provider adapters use ``resource`` for transaction-scoped
    persistence without exposing a database-specific type in this contract.
    """

    resource: Any

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        ...


class UnitOfWorkFactory(Protocol):
    """Creates a provider-neutral Unit of Work."""

    def __call__(self) -> UnitOfWork:
        ...
