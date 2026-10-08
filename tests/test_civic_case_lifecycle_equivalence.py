import json
import subprocess
from pathlib import Path

from src.core.case_lifecycle import CASE_STATUS_TRANSITIONS
from src.core.civic_case import CaseStatus


RUST_CRATE = Path(__file__).parents[1] / "crates" / "janavani-core"


def _python_matrix() -> dict[str, list[str]]:
    return {
        status.value: sorted(target.value for target in targets)
        for status, targets in CASE_STATUS_TRANSITIONS.items()
    }


def _rust_matrix() -> dict[str, list[str]]:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--example",
            "lifecycle_matrix",
            "--manifest-path",
            str(RUST_CRATE / "Cargo.toml"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    matrix = json.loads(result.stdout)
    return {status: sorted(targets) for status, targets in matrix.items()}


def test_python_contract_contains_every_case_status():
    assert set(_python_matrix()) == {status.value for status in CaseStatus}


def test_python_and_rust_lifecycle_matrices_are_equivalent():
    assert _rust_matrix() == _python_matrix()
