from __future__ import annotations

from src.storage.postgres_unit_of_work import PostgresUnitOfWork
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


class FakeConnection:
    def __init__(self):
        self.tx = FakeTransaction()
        self.closed = False

    def transaction(self):
        return self.tx

    def close(self):
        self.closed = True


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


def test_telegram_generation_dependencies_are_composed_once():
    deps = TelegramGenerationDependencies(
        case_repository=object(),
        artifact_repository=object(),
        blob_store=object(),
    )
    assert deps.case_repository is not None
    assert deps.artifact_repository is not None
    assert deps.blob_store is not None
