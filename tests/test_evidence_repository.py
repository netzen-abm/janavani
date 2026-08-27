from src.domain.evidence import Evidence, EvidenceKind, EvidenceStatus
from src.storage.evidence_repository import EvidenceRepository


def test_evidence_repository_round_trips_evidence(tmp_path):
    repository = EvidenceRepository(tmp_path / "evidence.jsonl")
    evidence = Evidence.create(
        "CASE-1",
        EvidenceKind.IMAGE,
        "Road damage photo",
        "citizen",
        content_ref="object://photo-1",
    ).with_status(EvidenceStatus.VERIFIED).add_provenance("source://record-1")

    repository.save(evidence)

    result = repository.get_by_id(evidence.evidence_id)
    assert result == evidence


def test_evidence_repository_lists_only_case_evidence(tmp_path):
    repository = EvidenceRepository(tmp_path / "evidence.jsonl")
    first = Evidence.create("CASE-1", EvidenceKind.IMAGE, "Photo", "citizen")
    second = Evidence.create("CASE-2", EvidenceKind.DOCUMENT, "Order", "citizen")
    repository.save(first)
    repository.save(second)

    assert repository.list_for_case("CASE-1") == [first]
    assert repository.list_for_case("missing") == []


def test_missing_evidence_returns_none(tmp_path):
    repository = EvidenceRepository(tmp_path / "evidence.jsonl")

    assert repository.get_by_id("EVD-MISSING") is None
