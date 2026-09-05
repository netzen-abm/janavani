#!/usr/bin/env python3
"""Run deterministic, non-destructive architecture guardrails."""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_LINE_LENGTH = 200
SKIP_PARTS = {".git", "target", "node_modules", "__pycache__"}
SCAN_SUFFIXES = {".py", ".rs", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".yml", ".yaml", ".sh"}


def is_scannable(path: pathlib.Path) -> bool:
    if not path.is_file():
        return False
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if "archive" in path.parts:
        return False
    return path.suffix.lower() in SCAN_SUFFIXES


def changed_paths() -> list[pathlib.Path]:
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    if event == "pull_request":
        base = os.environ.get("GITHUB_BASE_REF", "main")
        command = ["git", "diff", "--name-only", f"origin/{base}...HEAD"]
    else:
        command = ["git", "diff", "--name-only", "HEAD^", "HEAD"]
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    paths = []
    for name in result.stdout.splitlines():
        path = (ROOT / name).resolve()
        if path.is_relative_to(ROOT) and is_scannable(path):
            paths.append(path)
    return sorted(set(paths))


def line_length_failures(paths: list[pathlib.Path]) -> list[str]:
    failures = []
    for path in paths:
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
    try:
        changed = changed_paths()
    except subprocess.CalledProcessError as exc:
        print("ARCHITECTURE GUARD FAILED")
        print(f"unable to determine changed files: {exc}")
        return 1
    failures = line_length_failures(changed) + check_canonical_workspace()
    if failures:
        print("ARCHITECTURE GUARD FAILED")
        print("\n".join(failures))
        return 1
    print("ARCHITECTURE GUARD PASSED")
    print(f"Checked {len(changed)} changed source/config files; line length <= {MAX_LINE_LENGTH}.")
    print("Existing legacy line-length debt is not rewritten by this guard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
