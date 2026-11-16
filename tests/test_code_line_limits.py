"""Regression tests for the documented source line-count guideline."""
from pathlib import Path

from scripts.check_code_line_limits import (
    DOCUMENTED_OVERRIDES,
    documented_overrides,
    violations,
)


def test_cohesive_consent_boundary_exception_is_explicit_and_justified():
    reason = DOCUMENTED_OVERRIDES["src/capabilities/consent.py"]
    assert "scope/owner validation" in reason
    assert "do not split only to meet" in reason


def test_documented_exception_does_not_mask_other_oversized_files(tmp_path: Path):
    consent = tmp_path / "src" / "capabilities" / "consent.py"
    consent.parent.mkdir(parents=True)
    consent.write_text("\n".join(["line"] * 20), encoding="utf-8")

    unrelated = tmp_path / "src" / "capabilities" / "other.py"
    unrelated.write_text("\n".join(["line"] * 20), encoding="utf-8")

    assert documented_overrides(tmp_path, 10) == [
        ("src/capabilities/consent.py", 20, DOCUMENTED_OVERRIDES["src/capabilities/consent.py"])
    ]
    assert violations(tmp_path, 10) == [("src/capabilities/other.py", 20)]


def test_file_at_line_limit_is_not_reported(tmp_path: Path):
    path = tmp_path / "src" / "capabilities" / "small.py"
    path.parent.mkdir(parents=True)
    path.write_text("\n".join(["line"] * 10), encoding="utf-8")

    assert violations(tmp_path, 10) == []
