import json

from capabilities.tracking_file import LegacyComplaintTrackingCapability


def test_legacy_tracking_adapter_maps_complaint_to_case(tmp_path):
    path = tmp_path / "complaints.jsonl"
    path.write_text(
        json.dumps(
            {
                "complaint_id": "JNV-1234",
                "issue": "Broken road",
                "category": "roads",
                "department": "PWD",
                "district": "Kochi",
                "office": {"id": "7", "name": "PWD Office"},
                "created_at": "2026-08-30T10:00:00",
                "status": "Pending",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = LegacyComplaintTrackingCapability(str(path)).get_status("JNV-1234")

    assert result.ok is True
    assert result.case is not None
    assert result.case.case_id == "JNV-1234"
    assert result.case.case_type == "complaint"
    assert result.case.metadata["department"] == "PWD"
    assert result.case.jurisdiction["district"] == "Kochi"


def test_tracking_adapter_returns_safe_not_found(tmp_path):
    path = tmp_path / "complaints.jsonl"
    path.write_text("", encoding="utf-8")

    result = LegacyComplaintTrackingCapability(str(path)).get_status("UNKNOWN")

    assert result.ok is False
    assert result.error_code == "case_not_found"
    assert result.message == "Case not found."
