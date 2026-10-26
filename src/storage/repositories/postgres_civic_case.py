"""Standard PostgreSQL provider for the canonical CivicCase repository."""
from __future__ import annotations
import os
from typing import Any, Callable
from src.core.civic_case import CivicCase
from src.storage.repositories.civic_case import CivicCaseSummary
from src.storage.postgres_unit_of_work import bind_postgres_principal, postgres_unit_of_work_factory
from src.storage.unit_of_work import UnitOfWorkFactory
from src.storage.repositories.postgres_civic_case_codec import hydrate, now
from src.storage.repositories.postgres_civic_case_errors import PostgresCivicCaseConcurrencyError, PostgresCivicCasePersistenceError
from src.storage.repositories.postgres_civic_case_sql import (
    insert_case, persist_events, persist_refs, select_children, update_case,
)

class PostgresCivicCaseRepository:
    """Atomic PostgreSQL implementation of the CivicCaseRepository contract."""

    def __init__(
        self, connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None, unit_of_work_factory: UnitOfWorkFactory | None = None,
        principal_id: str | None = None,
    ) -> None:
        self._dsn = dsn or os.getenv("JANAVANI_POSTGRES_DSN")
        self._connection_factory = connection_factory
        self._principal_id = principal_id
        if self._connection_factory is None and not self._dsn:
            raise ValueError("Provide connection_factory or JANAVANI_POSTGRES_DSN")
        self._unit_of_work_factory = unit_of_work_factory or (
            postgres_unit_of_work_factory(self._connect, principal_id=principal_id)
        )

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise PostgresCivicCasePersistenceError(
                "Psycopg 3 is required for the PostgreSQL provider"
            ) from exc
        return psycopg.connect(self._dsn)

    def _resolve_principal(self, principal_id: str | None) -> str | None:
        """Prevent per-call identity from bypassing a provider-bound principal."""
        if self._principal_id is not None:
            if principal_id is not None and principal_id != self._principal_id:
                raise PermissionError("Repository principal does not match configured principal")
            return self._principal_id
        return principal_id

    @staticmethod
    def _row_factory() -> Any:
        try:
            from psycopg.rows import dict_row
        except ImportError:
            return None
        return dict_row

    def get(self, case_id: str, *, principal_id: str | None = None) -> CivicCase | None:
        try:
            effective_principal = self._resolve_principal(principal_id)
            with self._connect() as conn:
                with conn.transaction():
                    bind_postgres_principal(conn, effective_principal)
                    with conn.cursor(row_factory=self._row_factory()) as cur:
                        cur.execute("SELECT * FROM civic_cases WHERE case_id = %s", (case_id,))
                        row = cur.fetchone()
                        if row is None:
                            return None
                        children = [
                            select_children(cur, table, case_id)
                            for table in (
                                "civic_case_events", "civic_case_evidence_refs",
                                "civic_case_document_refs", "civic_case_consents",
                            )
                        ]
                        return hydrate(row, *children)
        except PostgresCivicCasePersistenceError:
            raise
        except Exception as exc:
            raise PostgresCivicCasePersistenceError(
                f"Failed to read Civic Case {case_id}"
            ) from exc

    def list_for_principal(
        self, principal_id: str, *, limit: int = 20
    ) -> list[CivicCaseSummary]:
        """Fetch bounded owner-scoped summaries in one SQL round trip."""
        if not isinstance(principal_id, str) or not principal_id.strip():
            return []
        try:
            effective = self._resolve_principal(principal_id)
            bounded_limit = max(1, min(int(limit), 50))
            with self._connect() as conn, conn.transaction():
                bind_postgres_principal(conn, effective)
                with conn.cursor(row_factory=self._row_factory()) as cur:
                    cur.execute(
                        """SELECT
                               c.case_id, c.case_type, c.status, c.created_at, c.updated_at,
                               COALESCE(e.last_activity_at, c.updated_at, c.created_at)
                                   AS last_activity_at,
                               COALESCE(v.evidence_count, 0) AS evidence_count,
                               COALESCE(d.document_count, 0) AS document_count
                           FROM civic_cases AS c
                           LEFT JOIN LATERAL (
                               SELECT MAX(occurred_at) AS last_activity_at
                               FROM civic_case_events WHERE case_id = c.case_id
                           ) AS e ON TRUE
                           LEFT JOIN LATERAL (
                               SELECT COUNT(*) AS evidence_count
                               FROM civic_case_evidence_refs WHERE case_id = c.case_id
                           ) AS v ON TRUE
                           LEFT JOIN LATERAL (
                               SELECT COUNT(*) AS document_count
                               FROM civic_case_document_refs WHERE case_id = c.case_id
                           ) AS d ON TRUE
                           WHERE c.created_by = %s
                           ORDER BY c.updated_at DESC NULLS LAST, c.created_at DESC NULLS LAST
                           LIMIT %s""",
                        (effective, bounded_limit),
                    )
                    return [
                        CivicCaseSummary(
                            case_id=str(row["case_id"]),
                            case_type=str(row["case_type"]),
                            status=str(row["status"]),
                            created_at=str(row["created_at"]) if row["created_at"] is not None else None,
                            updated_at=str(row["updated_at"]) if row["updated_at"] is not None else None,
                            last_activity_at=(
                                str(row["last_activity_at"])
                                if row["last_activity_at"] is not None else None
                            ),
                            evidence_count=int(row["evidence_count"]),
                            document_count=int(row["document_count"]),
                        )
                        for row in cur.fetchall()
                    ]
        except (PostgresCivicCasePersistenceError, PermissionError):
            raise
        except Exception as exc:
            raise PostgresCivicCasePersistenceError("Failed to list owned Civic Cases") from exc

    def save(self, case: CivicCase, *, principal_id: str | None = None) -> None:
        try:
            effective_principal = self._resolve_principal(principal_id)
            with self._unit_of_work_factory() as uow:
                conn = uow.connection
                bind_postgres_principal(conn, effective_principal)
                with conn.cursor(row_factory=self._row_factory()) as cur:
                    cur.execute(
                        "SELECT version, created_at FROM civic_cases WHERE case_id = %s FOR UPDATE",
                        (case.case_id,),
                    )
                    current = cur.fetchone()
                    timestamp = now()
                    if current is None:
                        version, created_at = 1, case.created_at or timestamp
                        insert_case(cur, case, created_at, timestamp, version)
                    else:
                        current_version = int(current["version"])
                        if case.version != current_version:
                            raise PostgresCivicCaseConcurrencyError(
                                f"Expected version {case.version}, found {current_version} for {case.case_id}"
                            )
                        version, created_at = current_version + 1, str(current["created_at"])
                        update_case(cur, case, created_at, timestamp, version, current_version)
                    persist_events(cur, case)
                    persist_refs(cur, case)
            case.created_at, case.updated_at, case.version = created_at, timestamp, version
        except (PostgresCivicCasePersistenceError, PostgresCivicCaseConcurrencyError, PermissionError):
            raise
        except Exception as exc:
            raise PostgresCivicCasePersistenceError(
                f"Failed to persist Civic Case {case.case_id}"
            ) from exc
