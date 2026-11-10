from pathlib import Path
import json
import re

from src.core.civic_case import CaseEventType, CaseStatus, CaseType
from src.core.case_events import CaseEvent
from src.core.case_helpers import validate_event_chain


def _enum_values(enum_cls):
    return {member.name: member.value for member in enum_cls}


def _rust_source() -> str:
    return Path("crates/janavani-core/src/civic_case.rs").read_text(encoding="utf-8")


def _rust_enum_values(source: str, enum_name: str):
    match = re.search(
        rf"pub enum {enum_name}\s*\{{(.*?)\n\}}",
        source,
        re.DOTALL,
    )
    assert match, f"Rust enum {enum_name} not found"
    values = {}
    for raw in match.group(1).splitlines():
        name = raw.strip().rstrip(",")
        if not name or name.startswith("#"):
            continue
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        values[snake.upper()] = snake
    return values


def test_python_rust_case_type_serialization_contract_matches():
    source = _rust_source()
    assert _enum_values(CaseType) == _rust_enum_values(source, "CaseType")


def test_python_rust_case_status_serialization_contract_matches():
    source = _rust_source()
    assert _enum_values(CaseStatus) == _rust_enum_values(source, "CaseStatus")


def test_python_rust_case_event_type_serialization_contract_matches():
    source = _rust_source()
    assert _enum_values(CaseEventType) == _rust_enum_values(source, "CaseEventType")


def _shared_event_vectors():
    path = Path("tests/fixtures/civic_case_event_contract_v1.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _python_events(raw_events):
    return [
        CaseEvent(
            event_id=item["event_id"],
            case_id=item["case_id"],
            event_type=CaseEventType(item["event_type"]),
            occurred_at=item["occurred_at"],
            actor_id=item.get("actor_id"),
            source_channel=item.get("source_channel"),
            source_ref=item.get("source_ref"),
            notes=item.get("notes"),
        )
        for item in raw_events
    ]


def test_python_event_chain_matches_shared_contract_vectors():
    vectors = _shared_event_vectors()
    assert vectors["contract_version"] == "1.0"
    assert validate_event_chain(_python_events(vectors["valid_chain"]))
    assert not validate_event_chain(_python_events(vectors["invalid_ack_then_submitted"]))
    assert not validate_event_chain(_python_events(vectors["invalid_duplicate_ids"]))
    assert not validate_event_chain(_python_events(vectors["invalid_mixed_cases"]))
