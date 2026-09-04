"""Provider-neutral Unit-of-Work boundary for atomic civic persistence."""
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Protocol, TypeVar

T = TypeVar("T")


class UnitOfWork(AbstractContextManager, Protocol):
    """Transaction boundary shared by storage providers.

    A Unit of Work begins one provider-owned transaction and yields a transaction
    context that coordinated repositories can use. The provider commits only
    when the context exits successfully; exceptions cause rollback.
    """

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        ...


class UnitOfWorkFactory(Protocol):
    """Creates a provider-neutral Unit of Work."""

    def __call__(self) -> UnitOfWork:
        ...
