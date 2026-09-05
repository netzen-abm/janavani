#!/usr/bin/env python3
"""Run deterministic, non-destructive architecture guardrails."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_LINE_LENGTH = 200
SKIP_PARTS = {".git", "target", "node_modules", "__pycache__"}
SCAN_SUFFIXES = {".py", ".rs", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".yml", ".yaml", ".sh"}


def iter_files() -> list[pathlib.Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if "archive" in path.parts:
            continue
        if path.suffix.lower() in SCAN_SUFFIXES:
            files.append(path)
    return sorted(files)


def check_line_lengths() -> list[str]:
    failures = []
    for path in iter_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            if len(line) > MAX_LINE_LENGTH:
                relative = path.relative_to(ROOT)
                failures.append(
                    f"{relative}:{number}: line length {len(line)} > {MAX_LINE_LENGTH}"
                )
    return failures


def check_canonical_workspace() -> list[str]:
    cargo = ROOT / "Cargo.toml"
    core = ROOT / "crates" / "janavani-core" / "Cargo.toml"
    application = ROOT / "crates" / "janavani-application" / "Cargo.toml"
    failures = []
    for path in (cargo, core, application):
        if not path.is_file():
            failures.append(f"missing canonical Rust file: {path.relative_to(ROOT)}")
    if cargo.is_file():
        text = cargo.read_text(encoding="utf-8")
        for member in ("crates/janavani-core", "crates/janavani-application"):
            if f'"{member}"' not in text:
                failures.append(f"canonical workspace member missing: {member}")
    return failures


def main() -> int:
    failures = check_line_lengths() + check_canonical_workspace()
    if failures:
        print("ARCHITECTURE GUARD FAILED")
        print("\n".join(failures))
        return 1
    print("ARCHITECTURE GUARD PASSED")
    print(f"Checked line length <= {MAX_LINE_LENGTH} and canonical workspace presence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
