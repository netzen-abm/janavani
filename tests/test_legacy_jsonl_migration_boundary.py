from pathlib import Path

from src.migration.legacy_jsonl import LegacyJsonlSource


def test_validate_empty_preserved_source_is_valid(tmp_path: Path) -> None:
    source = tmp_path / "legacy.jsonl"
    source.write_text("\n", encoding="utf-8")

    report = LegacyJsonlSource(source).validate()

    assert report.valid
    assert report.records == ()
    assert report.issues == ()


def test_validate_collects_invalid_json_without_stopping(tmp_path: Path) -> None:
    source = tmp_path / "legacy.jsonl"
    source.write_text(
        '{"id": "1"}\nnot-json\n["wrong-shape"]\n',
        encoding="utf-8",
    )

    report = LegacyJsonlSource(source).validate()

    assert not report.valid
    assert [record.value for record in report.records] == [{"id": "1"}]
    assert [issue.line_number for issue in report.issues] == [2, 3]


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    report = LegacyJsonlSource(tmp_path / "missing.jsonl").validate()

    assert not report.valid
    assert report.issues[0].line_number == 0


def test_iter_records_does_not_modify_source(tmp_path: Path) -> None:
    source = tmp_path / "legacy.jsonl"
    original = '{"id": "1"}\n'
    source.write_text(original, encoding="utf-8")

    records = list(LegacyJsonlSource(source).iter_records())

    assert len(records) == 1
    assert source.read_text(encoding="utf-8") == original
