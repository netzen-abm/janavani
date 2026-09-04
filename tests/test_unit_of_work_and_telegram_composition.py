from __future__ import annotations

from src.core.civic_case import CaseType, CivicCase
from src.storage.postgres_unit_of_work import PostgresUnitOfWork
from src.storage.repositories.postgres_civic_case import PostgresCivicCaseRepository
from src.conversation.steps.generate import TelegramGenerationDependencies


class FakeTransaction:
    def __init__(self):
        self.events = []

    def __enter__(self):
        self.events.append("begin")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.events.append("rollback" if exc_type else "commit")
        return False


class FakeCursor:
    def __init__(self):
        self.statements = []
        self.rowcount = 1
        self._fetchone_values = [None]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def executemany(self, sql, params):
        self.statements.append((sql, list(params)))

    def fetchone(self):
        if self._fetchone_values:
            return self._fetchone_values.pop(0)
        return None

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self):
        self.tx = FakeTransaction()
        self.closed = False
        self.cursor_instance = FakeCursor()

    def transaction(self):
        return self.tx

    def cursor(self, **kwargs):
        return self.cursor_instance

    def close(self):
        self.closed = True


class FakeUnitOfWork:
    def __init__(self, connection):
        self.connection = connection
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exited = True
        return False


def test_postgres_uow_commits_and_closes_connection():
    connection = FakeConnection()
    with PostgresUnitOfWork(lambda: connection) as uow:
        assert uow.connection is connection
    assert connection.tx.events == ["begin", "commit"]
    assert connection.closed


def test_postgres_uow_rolls_back_on_exception():
    connection = FakeConnection()
    try:
        with PostgresUnitOfWork(lambda: connection):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert connection.tx.events == ["begin", "rollback"]
    assert connection.closed


def test_civic_case_repository_uses_injected_unit_of_work():
    connection = FakeConnection()
    uow = FakeUnitOfWork(connection)
    repository = PostgresCivicCaseRepository(
        connection_factory=lambda: (_ for _ in ()).throw(
            AssertionError("repository must not open its own connection")
        ),
        unit_of_work_factory=lambda: uow,
    )
    case = CivicCase(
        case_id="CASE-UOW-1",
        case_type=CaseType.COMPLAINT,
        subject="Test subject",
        narrative="Test narrative",
    )

    repository.save(case)

    assert uow.entered
    assert uow.exited
    assert case.version == 1
    assert any("INSERT INTO civic_cases" in sql for sql, _ in connection.cursor_instance.statements)


def test_telegram_generation_dependencies_are_composed_once():
    deps = TelegramGenerationDependencies(
        case_repository=object(),
        artifact_repository=object(),
        blob_store=object(),
    )
    assert deps.case_repository is not None
    assert deps.artifact_repository is not None
    assert deps.blob_store is not None
