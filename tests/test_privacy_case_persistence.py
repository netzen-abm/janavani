from src.core.civic_case import CaseType, CivicCase
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.postgres_civic_case_codec import case_values


def test_in_memory_case_persistence_redacts_citizen_content():
    repository = InMemoryCivicCaseRepository()
    case = CivicCase(
        case_id="case-privacy",
        case_type=CaseType.COMPLAINT,
        subject="My private subject",
        narrative="My sensitive citizen narrative",
        created_by="opaque-principal",
    )

    repository.save(case)
    stored = repository.get(case.case_id)

    assert stored is not None
    assert stored.subject == CaseType.COMPLAINT.value
    assert stored.narrative == ""


def test_postgres_case_values_never_include_citizen_subject_or_narrative():
    case = CivicCase(
        case_id="case-privacy",
        case_type=CaseType.COMPLAINT,
        subject="Private subject",
        narrative="Private narrative",
        created_by="opaque-principal",
    )

    values = case_values(
        case,
        created_at="2026-10-07T00:00:00+00:00",
        updated_at="2026-10-07T00:00:00+00:00",
        version=1,
    )

    assert values[1] == CaseType.COMPLAINT.value
    assert values[2] == CaseType.COMPLAINT.value
    assert values[3] == ""
    assert "Private subject" not in values
    assert "Private narrative" not in values
