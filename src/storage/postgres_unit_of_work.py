"""PostgreSQL implementation of the shared Unit-of-Work contract."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from src.storage.unit_of_work import UnitOfWork


class PostgresSecurityContext:
    """Transaction-local PostgreSQL security context for trusted principals."""

    def __init__(self, connection: Any, principal_id: str | None) -> None:
        self.connection = connection
        self.principal_id = principal_id

    def bind(self) -> None:
        if self.principal_id is None:
            return
        if not isinstance(self.principal_id, str) or not self.principal_id.strip():
            raise ValueError("principal_id must be a non-empty string")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('janavani.principal_id', %s, true)",
                (self.principal_id,),
            )


def bind_postgres_principal(connection: Any, principal_id: str | None) -> None:
    """Bind a trusted principal for the current PostgreSQL transaction."""
    PostgresSecurityContext(connection, principal_id).bind()


class PostgresUnitOfWork(UnitOfWork):
    """Own one PostgreSQL connection and its transaction lifecycle."""

    def __init__(self, connection_factory: Callable[[], Any], *, principal_id: str | None = None) -> None:
        self._connection_factory = connection_factory
        self._principal_id = principal_id
        self.resource: Any | None = None
        self._transaction: Any | None = None

    @property
    def connection(self) -> Any | None:
        """Compatibility alias for PostgreSQL-specific repository code."""
        return self.resource

    def __enter__(self) -> Self:
        self.resource = self._connection_factory()
        self._transaction = self.resource.transaction()
        self._transaction.__enter__()
        bind_postgres_principal(self.resource, self._principal_id)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        try:
            if self._transaction is None:
                return None
            return self._transaction.__exit__(exc_type, exc_value, traceback)
        finally:
            self._transaction = None
            if self.resource is not None:
                close = getattr(self.resource, "close", None)
                if close is not None:
                    close()
                self.resource = None


def postgres_unit_of_work_factory(
    connection_factory: Callable[[], Any],
    *,
    principal_id: str | None = None,
) -> Callable[[], PostgresUnitOfWork]:
    """Create an injectable Unit-of-Work factory for a PostgreSQL provider."""
    return lambda: PostgresUnitOfWork(connection_factory, principal_id=principal_id)
