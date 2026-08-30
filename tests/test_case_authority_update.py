import json

from capabilities.case_legacy import FileCaseCapability


def test_case_can_attach_selected_authority(tmp_path):
    path = tmp_path / "complaints.jsonl"
    capability = FileCaseCapability(str(path))
    created = capability.create(
        case_type="complaint",
        issue="Broken road",
        metadata={"district": "Kochi"},
    )
    assert created.ok

    authority = {
        "id": "7",
        "name": "PWD Office",
        "type": "PWD",
        "jurisdiction": "Kochi",
        "source": "directory",
    }
    updated = capability.update(created.case.case_id, office=authority, district="Kochi")

    assert updated.ok
    assert updated.case is not None
    assert updated.case.authority == authority
    assert updated.case.jurisdiction["district"] == "Kochi"
