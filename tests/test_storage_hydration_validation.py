import pytest

from src.storage.hydration import (
    case_from_row,
    evidence_from_row,
    submission_from_row,
)


def test_case_hydration_rejects_missing_id() -> None:
    with pytest.raises(ValueError, match="id"):
        case_from_row({"issue": "missing id"})


def test_evidence_hydration_rejects_missing_case() -> None:
    with pytest.raises(ValueError, match="case_id"):
        evidence_from_row(
            {
                "evidence_id": "E-1",
                "kind": "document",
                "title": "Order",
                "source": "citizen",
            }
        )


def test_submission_hydration_rejects_missing_operation_id() -> None:
    with pytest.raises(ValueError, match="operation_id"):
        submission_from_row(
            {
                "submission_id": "SUB-1",
                "case_id": "CASE-1",
                "destination_ref": "AUTH-1",
            }
        )
