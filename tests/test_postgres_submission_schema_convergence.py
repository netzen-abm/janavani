import inspect

from src.storage.repositories import postgres_submission_sql
from src.storage.repositories.postgres_submission import PostgresSubmissionRepository


def test_submission_schema_ownership_stays_with_migrations():
    source = inspect.getsource(postgres_submission_sql.initialize)
    assert "CREATE TABLE" not in source
    assert "CREATE INDEX" not in source
    assert "information_schema.tables" in source


def test_submission_repository_keeps_a_schema_validation_boundary():
    source = inspect.getsource(PostgresSubmissionRepository._initialize)
    assert "initialize(connection)" in source
