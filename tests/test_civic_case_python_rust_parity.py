from pathlib import Path
import re

from src.core.civic_case import CaseEventType, CaseStatus, CaseType


def _enum_values(enum_cls):
    return {member.name: member.value for member in enum_cls}


def _rust_source() -> str:
    return Path("crates/janavani-core/src/civic_case.rs").read_text(encoding="utf-8")


def _rust_enum_values(source: str, enum_name: str):
    match = re.search(
        rf"pub enum {enum_name}\\s*\\{{(.*?)\\n\\}}",
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
        values[name] = snake
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
