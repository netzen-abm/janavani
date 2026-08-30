import json

from capabilities.feedback_file import JsonlFeedbackCapability


def test_feedback_capability_records_rating(tmp_path):
    path = tmp_path / "ratings.jsonl"
    result = JsonlFeedbackCapability(str(path)).submit_rating(
        authority_id="3",
        rating=4,
        comment="Service was helpful",
    )

    assert result.ok is True
    assert result.feedback_id is not None

    record = json.loads(path.read_text(encoding="utf-8").strip())
    assert record["feedback_id"] == result.feedback_id
    assert record["authority_id"] == "3"
    assert record["rating"] == 4
    assert record["comment"] == "Service was helpful"


def test_feedback_capability_rejects_invalid_rating(tmp_path):
    path = tmp_path / "ratings.jsonl"
    result = JsonlFeedbackCapability(str(path)).submit_rating(
        authority_id="3",
        rating=7,
    )

    assert result.ok is False
    assert result.error_code == "invalid_rating"
    assert not path.exists()
