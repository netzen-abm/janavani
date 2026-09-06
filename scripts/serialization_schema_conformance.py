"""Validate canonical case serialization and database field contracts."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_CASE = ROOT / "src/core/civic_case.py"
RUST_CASE = ROOT / "crates/janavani-core/src/civic_case.rs"
DB_CONTRACT = ROOT / "docs/architecture/CIVIC_CASE_DATABASE_CONTRACT.md"

CASE_FIELDS = (
    "case_id",
    "case_type",
    "subject",
    "narrative",
    "created_by",
    "jurisdiction",
    "related_organisation_id",
    "related_office_id",
    "related_official_id",
    "related_representative_id",
    "claims",
    "evidence_refs",
    "document_refs",
    "consent_refs",
    "status",
    "events",
    "created_at",
    "updated_at",
    "version",
)
EVENT_FIELDS = (
    "event_id",
    "case_id",
    "event_type",
    "occurred_at",
    "actor_id",
    "source_channel",
    "source_ref",
    "notes",
)
CASE_DB_FIELDS = {
    "case_id": "civic_cases.case_id",
    "case_type": "civic_cases.case_type",
    "subject": "civic_cases.subject",
    "narrative": "civic_cases.narrative",
    "created_by": "civic_cases.created_by",
    "jurisdiction": "civic_cases.jurisdiction_json",
    "related_organisation_id": "civic_cases.related_organisation_id",
    "related_office_id": "civic_cases.related_office_id",
    "related_official_id": "civic_cases.related_official_id",
    "related_representative_id": "civic_cases.related_representative_id",
    "claims": "civic_cases.subject_claims_json",
    "status": "civic_cases.status",
    "created_at": "civic_cases.created_at",
    "updated_at": "civic_cases.updated_at",
    "version": "civic_cases.version",
}


def dataclass_fields(source: str, class_name: str) -> set[str]:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                item.target.id
                for item in node.body
                if isinstance(item, ast.AnnAssign)
                and isinstance(item.target, ast.Name)
            }
    raise ValueError(f"Missing Python class: {class_name}")


def rust_struct_fields(source: str, struct_name: str) -> set[str]:
    match = re.search(
        rf"pub struct {struct_name} \{{(?P<body>.*?)\n\}}",
        source,
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"Missing Rust struct: {struct_name}")
    return set(
        re.findall(
            r"^    pub ([A-Za-z0-9_]+):",
            match.group("body"),
            re.MULTILINE,
        )
    )


def assert_equal(label: str, actual: set[str], expected: tuple[str, ...]) -> None:
    wanted = set(expected)
    if actual != wanted:
        missing = sorted(wanted - actual)
        extra = sorted(actual - wanted)
        raise ValueError(f"{label} mismatch; missing={missing}; extra={extra}")


def check_db_mapping(contract: str) -> None:
    for field, column in CASE_DB_FIELDS.items():
        pattern = rf"\| `{re.escape(field)}` \| `?[^|]+`? \|"
        if not re.search(pattern, contract):
            raise ValueError(f"Database contract is missing field: {field}")
        if column.split(".", 1)[1] not in contract:
            raise ValueError(f"Database mapping is missing column: {column}")


def main() -> None:
    py_source = PY_CASE.read_text(encoding="utf-8")
    rust_source = RUST_CASE.read_text(encoding="utf-8")
    contract = DB_CONTRACT.read_text(encoding="utf-8")

    assert_equal(
        "Python CivicCase",
        dataclass_fields(py_source, "CivicCase"),
        CASE_FIELDS,
    )
    assert_equal(
        "Python CaseEvent",
        dataclass_fields(py_source, "CaseEvent"),
        EVENT_FIELDS,
    )
    assert_equal(
        "Rust CivicCase",
        rust_struct_fields(rust_source, "CivicCase"),
        CASE_FIELDS,
    )
    assert_equal(
        "Rust CaseEvent",
        rust_struct_fields(rust_source, "CaseEvent"),
        EVENT_FIELDS,
    )
    check_db_mapping(contract)
    print("Serialization/schema conformance: PASS")


if __name__ == "__main__":
    main()
