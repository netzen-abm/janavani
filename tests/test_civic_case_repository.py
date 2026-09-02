from src.core.civic_case import CaseType, CivicCase
from src.storage.repositories.civic_case import (
    InMemoryCivicCaseRepository,
)


def make_case(case_id: str = "case-1") -> CivicCase:
    return CivicCase(
        case_id=case_id,
        case_type=CaseType.COMPLAINT,
        subject="Broken road",
        narrative="The road is damaged.",
    )


def test_in_memory_repository_round_trip() -> None:
    repository = InMemoryCivicCaseRepository()
    case = make_case()

    repository.save(case)

    assert repository.get(case.case_id) is case


def test_in_memory_repository_missing_case() -> None:
    repository = InMemoryCivicCaseRepository()

    assert repository.get("missing") is None


def test_in_memory_repository_can_be_cleared() -> None:
    repository = InMemoryCivicCaseRepository()
    case = make_case()
    repository.save(case)

    repository.clear()

    assert repository.get(case.case_id) is None
