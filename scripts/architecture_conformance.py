#!/usr/bin/env python3
"""Verify cross-language architecture contracts without mutation."""
from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_LIFECYCLE = ROOT / "src/core/case_lifecycle.py"
PY_DOMAIN = ROOT / "src/core/civic_case.py"
RUST_CORE = ROOT / "crates/janavani-core/src/lib.rs"


def python_enum_members(path: pathlib.Path, name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return {
                target.id
                for item in node.body
                if isinstance(item, ast.Assign)
                for target in item.targets
                if isinstance(target, ast.Name)
            }
    raise ValueError(f"missing Python enum: {name}")


def rust_enum_members(text: str, name: str) -> set[str]:
    match = re.search(rf"pub enum {name} \{{(.*?)\n\}}", text, re.S)
    if not match:
        raise ValueError(f"missing Rust enum: {name}")
    return set(re.findall(r"^\s*([A-Z][A-Za-z0-9_]*)\s*,", match.group(1), re.M))


def rust_name(python_name: str) -> str:
    return "".join(part.title() for part in python_name.split("_"))


def attr_name(node: ast.AST) -> str:
    if not isinstance(node, ast.Attribute):
        raise ValueError("lifecycle key is not an enum member")
    return node.attr


def lifecycle_assignment(node: ast.AST) -> ast.Dict | None:
    if isinstance(node, ast.Assign):
        targets = node.targets
        value = node.value
    elif isinstance(node, ast.AnnAssign):
        targets = [node.target]
        value = node.value
    else:
        return None
    if not any(
        isinstance(target, ast.Name)
        and target.id == "CASE_STATUS_TRANSITIONS"
        for target in targets
    ):
        return None
    if not isinstance(value, ast.Dict):
        raise ValueError("lifecycle contract is not a dictionary")
    return value


def lifecycle_pairs() -> set[tuple[str, str]]:
    tree = ast.parse(PY_LIFECYCLE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        value = lifecycle_assignment(node)
        if value is None:
            continue
        pairs = set()
        for key, target_value in zip(value.keys, value.values):
            if not isinstance(target_value, ast.Call) or not target_value.args:
                raise ValueError("lifecycle targets are not statically represented")
            source = attr_name(key)
            targets = target_value.args[0]
            if not isinstance(targets, ast.Set):
                raise ValueError("lifecycle targets are not a set")
            pairs.update((source, attr_name(target)) for target in targets.elts)
        return pairs
    raise ValueError("missing CASE_STATUS_TRANSITIONS")


def rust_lifecycle_pairs(text: str) -> set[tuple[str, str]]:
    match = re.search(r"pub fn can_transition\(self, target: Self\).*?\n    \}\n", text, re.S)
    if not match:
        raise ValueError("missing Rust can_transition")
    body = match.group(0)
    pairs: set[tuple[str, str]] = set()
    for source, targets in re.findall(r"\n            (\w+) => matches!\(target, ([^\n]+)\),", body):
        pairs.update((source, target) for target in re.findall(r"\b([A-Z][A-Za-z0-9_]*)\b", targets))
    block = re.search(
        r"Acknowledged => \{\s*matches!\(target, ([^\n]+)\)\s*\}", body
    )
    if block:
        pairs.update(
            ("Acknowledged", target)
            for target in re.findall(r"\b([A-Z][A-Za-z0-9_]*)\b", block.group(1))
        )
    return pairs


def check_enum_parity() -> list[str]:
    rust = RUST_CORE.read_text(encoding="utf-8")
    failures = []
    for name in ("CaseStatus", "CaseEventType"):
        python = python_enum_members(PY_DOMAIN, name)
        actual = rust_enum_members(rust, name)
        expected = {rust_name(item) for item in python}
        if expected != actual:
            failures.append(f"enum parity mismatch: {name}")
    return failures


def check_lifecycle_parity() -> list[str]:
    rust = RUST_CORE.read_text(encoding="utf-8")
    expected = {(rust_name(a), rust_name(b)) for a, b in lifecycle_pairs()}
    actual = rust_lifecycle_pairs(rust)
    return [] if expected == actual else ["lifecycle transition parity mismatch"]


def check_legacy_references() -> list[str]:
    failures = []
    suffixes = {".py", ".rs", ".js", ".ts", ".tsx", ".jsx", ".yml", ".yaml", ".sh"}
    skipped = {".git", "target", "node_modules", "__pycache__", "archive"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if any(part in skipped for part in path.parts):
            continue
        if path.name == "architecture_conformance.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"(?:janavani_v2|janavani_v3)", text):
            failures.append(f"active legacy-generation reference: {path.relative_to(ROOT)}")
    return failures


def main() -> int:
    try:
        failures = check_enum_parity() + check_lifecycle_parity() + check_legacy_references()
    except (OSError, SyntaxError, ValueError) as exc:
        print("ARCHITECTURE CONFORMANCE FAILED")
        print(f"unable to evaluate contract: {exc}")
        return 1
    if failures:
        print("ARCHITECTURE CONFORMANCE FAILED")
        print("\n".join(failures))
        return 1
    print("ARCHITECTURE CONFORMANCE PASSED")
    print("Rust/Python enum and lifecycle parity verified; no active legacy references found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
