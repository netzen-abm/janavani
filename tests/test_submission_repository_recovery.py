from src.core.submission import SubmissionRecord
from src.storage.repositories.submission import InMemorySubmissionRepository


def make_submission(submission_id: str, state: str) -> SubmissionRecord:
    return SubmissionRecord(
        submission_id=submission_id,
        case_id="case_1",
        destination_ref="office_1",
        document_ref="doc_1",
        channel="telegram",
        state=state,
        created_at="2026-09-12T10:00:00+00:00",
        updated_at="2026-09-12T10:00:00+00:00",
    )


def test_list_recoverable_returns_only_in_flight_records():
    repository = InMemorySubmissionRepository()
    repository.save(make_submission("sub_1", "submitting"))
    repository.save(make_submission("sub_2", "failed"))
    repository.save(make_submission("sub_3", "submitted"))

    recoverable = repository.list_recoverable()

    assert tuple(item.submission_id for item in recoverable) == ("sub_1",)
