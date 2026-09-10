from unittest.mock import MagicMock

from src.core.submission import SubmissionRecord
from src.storage.repositories.postgres_submission import PostgresSubmissionRepository


def make_submission() -> SubmissionRecord:
    return SubmissionRecord.new(
        submission_id="sub-1",
        case_id="case-1",
        destination_ref="office-1",
        document_ref="doc-1",
        channel="web",
    )


def configured_connection():
    connection = MagicMock()
    connection.__enter__.return_value = connection
    cursor = connection.cursor.return_value.__enter__.return_value
    connection.transaction.return_value.__enter__.return_value = connection
    return connection, cursor


def test_postgres_submission_repository_requires_configuration():
    try:
        PostgresSubmissionRepository(connection_factory=None, dsn=None)
    except ValueError as exc:
        assert "DSN or connection factory" in str(exc)
    else:
        raise AssertionError("expected configuration failure")


def test_save_writes_submission_fields():
    connection, cursor = configured_connection()
    repository = PostgresSubmissionRepository(connection_factory=lambda: connection)

    repository.save(make_submission())

    assert any("INSERT INTO civic_case_submissions" in call.args[0] for call in cursor.execute.call_args_list)


def test_get_hydrates_submission():
    connection, cursor = configured_connection()
    submission = make_submission()
    cursor.fetchone.return_value = (
        submission.submission_id, submission.case_id, submission.destination_ref,
        submission.document_ref, submission.channel, submission.state,
        submission.attempted_at, submission.submitted_at, submission.acknowledged_at,
        submission.external_reference, submission.ack_ref, submission.error_code,
        submission.retry_count, submission.created_at, submission.updated_at,
        submission.version,
    )
    repository = PostgresSubmissionRepository(connection_factory=lambda: connection)

    result = repository.get("sub-1")

    assert result == submission


def test_list_for_case_returns_hydrated_records():
    connection, cursor = configured_connection()
    submission = make_submission()
    cursor.fetchall.return_value = [(
        submission.submission_id, submission.case_id, submission.destination_ref,
        submission.document_ref, submission.channel, submission.state,
        submission.attempted_at, submission.submitted_at, submission.acknowledged_at,
        submission.external_reference, submission.ack_ref, submission.error_code,
        submission.retry_count, submission.created_at, submission.updated_at,
        submission.version,
    )]
    repository = PostgresSubmissionRepository(connection_factory=lambda: connection)

    result = repository.list_for_case("case-1")

    assert result == (submission,)
