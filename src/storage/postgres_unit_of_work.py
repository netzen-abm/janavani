"""PostgreSQL implementation of the shared Unit-of-Work contract."""
from __future__ import annotations

from typing import Any, Callable

from src.storage.unit_of_work import UnitOfWork


class PostgresUnitOfWork(UnitOfWork):
    """Own one PostgreSQL connection and its transaction lifecycle."""

    def __init__(self, connection_factory: Callable[[], Any]) -> None:
        self._connection_factory = connection_factory
        self.connection: Any | None = None
        self._transaction: Any | None = None

    def __enter__(self) -> "PostgresUnitOfWork":
        self.connection = self._connection_factory()
        self._transaction = self.connection.transaction()
        self._transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        try:
            if self._transaction is None:
                return None
            return self._transaction.__exit__(exc_type, exc_value, traceback)
        finally:
            self._transaction = None
            if self.connection is not None:
                self.connection.close()
                self.connection = None


def postgres_unit_of_work_factory(
    connection_factory: Callable[[], Any],
) -> Callable[[], PostgresUnitOfWork]:
    """Create an injectable Unit-of-Work factory for a PostgreSQL provider."""
    return lambda: PostgresUnitOfWork(connection_factory)
