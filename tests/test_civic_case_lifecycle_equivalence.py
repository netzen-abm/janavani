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
    probe = r'''
use janavani_core::CaseStatus;
fn main() {
    use CaseStatus::*;
    let statuses = [Draft, Review, Ready, Submitting, Queued, Submitted, Acknowledged,
        FollowUp, InProgress, Responded, Resolved, Escalated, Closed, Archived];
    let mut out = String::from("{");
    for (i, current) in statuses.iter().enumerate() {
        if i > 0 { out.push(','); }
        out.push_str(&format!("\"{}\":[", serde_json::to_string(current).unwrap().trim_matches('"')));
        let mut first = true;
        for target in statuses.iter() {
            if current.can_transition(*target) {
                if !first { out.push(','); }
                first = false;
                out.push_str(&serde_json::to_string(target).unwrap());
            }
        }
        out.push(']');
    }
    out.push('}');
    println!("{out}");
}
'''
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Cargo.toml").write_text(
            "[package]\nname='lifecycle_probe'\nversion='0.1.0'\nedition='2021'\n\n"
            "[dependencies]\njanavani-core={path='" + str(RUST_CRATE) + "'}\n"
            "serde_json='1'\n"
        )
        src = root / "src"
        src.mkdir()
        (src / "main.rs").write_text(probe)
        result = subprocess.run(
            ["cargo", "run", "--quiet", "--manifest-path", str(root / "Cargo.toml")],
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
