"""Contract tests for the provider-neutral complaint repository."""

from pathlib import Path

from src.storage.complaint_repository import ComplaintRepository


def test_repository_round_trips_complaint(tmp_path: Path):
    repository = ComplaintRepository(tmp_path / "complaints.jsonl")
    record = {
        "complaint_id": "CMP-001",
        "issue": "Streetlight failure",
        "status": "Pending",
    }

    repository.save(record)

    result = repository.get_by_id("CMP-001")

    assert result is not None
    assert result["complaint_id"] == "CMP-001"
    assert result["issue"] == "Streetlight failure"
    assert result["status"] == "Pending"
    assert result["created_at"].endswith("+00:00")


def test_repository_returns_none_for_missing_complaint(tmp_path: Path):
    repository = ComplaintRepository(tmp_path / "complaints.jsonl")

    assert repository.get_by_id("missing") is None


def test_repository_ignores_blank_lines(tmp_path: Path):
    path = tmp_path / "complaints.jsonl"
    path.write_text("\n\n", encoding="utf-8")
    repository = ComplaintRepository(path)

    assert repository.get_by_id("missing") is None
