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

    stored = repository.get(case.case_id)
    assert stored is not case
    assert stored.subject == CaseType.COMPLAINT.value
    assert stored.narrative == ""



def test_in_memory_repository_increments_versions_and_rejects_stale_writes() -> None:
    import pytest

    repository = InMemoryCivicCaseRepository()
    repository.save(make_case())
    current = repository.get("case-1")
    stale = repository.get("case-1")
    assert current is not None and stale is not None

    current.add_evidence(
        "evidence-current",
        event_id="event-current",
        occurred_at="2026-11-25T00:00:00Z",
    )
    repository.save(current)
    assert current.version == 2

    stale.add_evidence(
        "evidence-stale",
        event_id="event-stale",
        occurred_at="2026-11-25T00:00:01Z",
    )
    with pytest.raises(RuntimeError, match="Expected Case version"):
        repository.save(stale)

    persisted = repository.get("case-1")
    assert persisted is not None
    assert persisted.version == 2
    assert persisted.evidence_refs == ["evidence-current"]
    assert [event.event_id for event in persisted.events] == ["event-current"]


def test_in_memory_repository_missing_case() -> None:
    repository = InMemoryCivicCaseRepository()

    assert repository.get("missing") is None


def test_in_memory_repository_can_be_cleared() -> None:
    repository = InMemoryCivicCaseRepository()
    case = make_case()
    repository.save(case)

    repository.clear()

    assert repository.get(case.case_id) is None
