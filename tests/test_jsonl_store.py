"""Regression tests for shared JSONL persistence operations."""
import json

import pytest

from src.storage.jsonl_store import read_jsonl_records, write_jsonl_records


def test_read_jsonl_skips_blank_lines(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text('{"id": 1}\n\n{"id": 2}\n', encoding="utf-8")
    assert read_jsonl_records(path) == [{"id": 1}, {"id": 2}]


def test_write_jsonl_round_trips_records(tmp_path):
    path = tmp_path / "records.jsonl"
    records = [{"complaint_id": "JNV-1", "status": "submitted"}]
    write_jsonl_records(path, records)
    assert read_jsonl_records(path) == records


def test_write_jsonl_replaces_existing_contents(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text('{"old": true}\n', encoding="utf-8")
    write_jsonl_records(path, [{"new": True}])
    assert path.read_text(encoding="utf-8") == json.dumps({"new": True}) + "\n"


def test_read_jsonl_raises_on_malformed_record(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        read_jsonl_records(path)

 

def test_update_jsonl_records_updates_all_matching_records(tmp_path):
    from src.storage.jsonl_store import update_jsonl_records

    path = tmp_path / "records.jsonl"
    write_jsonl_records(path, [
        {"complaint_id": "JNV-1", "status": "submitted"},
        {"complaint_id": "JNV-1", "status": "submitted"},
        {"complaint_id": "JNV-2", "status": "submitted"},
    ])

    assert update_jsonl_records(
        path, "complaint_id", "JNV-1", {"status": "acknowledged"}
    )
    assert [r["status"] for r in read_jsonl_records(path)] == [
        "acknowledged", "acknowledged", "submitted"
    ]


def test_update_jsonl_records_returns_false_when_not_found(tmp_path):
    from src.storage.jsonl_store import update_jsonl_records

    path = tmp_path / "records.jsonl"
    write_jsonl_records(path, [{"complaint_id": "JNV-2", "status": "submitted"}])

    assert not update_jsonl_records(
        path, "complaint_id", "JNV-1", {"status": "acknowledged"}
    )
