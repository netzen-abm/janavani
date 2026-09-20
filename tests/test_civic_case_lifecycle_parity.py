import json
from pathlib import Path

from src.core.case_lifecycle import CASE_STATUS_TRANSITIONS
from src.core.civic_case import CaseStatus

FIXTURE = Path(__file__).parent / "fixtures" / "civic_case_transitions.json"


def test_python_lifecycle_matches_canonical_transition_fixture():
    expected = json.loads(FIXTURE.read_text(encoding="utf-8"))
    actual = {
        status.value: sorted(target.value for target in targets)
        for status, targets in CASE_STATUS_TRANSITIONS.items()
    }
    assert actual == expected
    assert set(actual) == {status.value for status in CaseStatus}
