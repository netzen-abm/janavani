#!/usr/bin/env python3
"""Produce deterministic, non-destructive evidence for legacy archiving."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIRS = ("janavani_v2", "janavani_v3")
SKIP_PARTS = {".git", "target", "node_modules", "__pycache__", "archive"}
SCANNABLE = {".py", ".rs", ".js", ".ts", ".tsx", ".jsx", ".yml", ".yaml", ".sh", ".toml"}
EVIDENCE_SCRIPTS = {
    "archive_safety_evidence.py",
    "architecture_conformance.py",
}


def git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def active_files(files: list[Path]) -> list[Path]:
    return [
        path
        for path in files
        if path.suffix in SCANNABLE
        and not any(part in SKIP_PARTS for part in path.parts)
        and not any(part in LEGACY_DIRS for part in path.parts)
        and path.name not in EVIDENCE_SCRIPTS
    ]


def legacy_files(files: list[Path], legacy: str) -> list[Path]:
    return [path for path in files if legacy in path.parts]


def active_references(files: list[Path], legacy: str) -> list[str]:
    matches: list[str] = []
    for path in active_files(files):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if legacy in text:
            matches.append(path.relative_to(ROOT).as_posix())
    return matches


def capability_files(files: list[Path], legacy: str) -> list[str]:
    paths = legacy_files(files, legacy)
    return [path.relative_to(ROOT).as_posix() for path in paths]


def main() -> int:
    try:
        files = git_files()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ARCHIVE SAFETY EVIDENCE FAILED: {exc}")
        return 1

    print("ARCHIVE SAFETY EVIDENCE")
    print("=======================")
    print("Non-destructive evidence only; no archive or delete action is performed.")
    print("")

    blocked = False
    for legacy in LEGACY_DIRS:
        paths = capability_files(files, legacy)
        refs = active_references(files, legacy)
        print(f"[{legacy}]")
        print(f"tracked files: {len(paths)}")
        print(f"active references: {len(refs)}")
        if refs:
            blocked = True
            print("status: BLOCKED — active references require migration evidence")
            for ref in refs:
                print(f"  reference: {ref}")
        else:
            print("status: REFERENCE-CLEAN — capability review still required")
        print("")

    print("ARCHIVE DECISION")
    print("----------------")
    print("A reference-clean result is not an archive approval.")
    print("Unique capabilities, build paths, deployment use, and retention needs")
    print("must be reviewed before any archive or deletion change.")
    if blocked:
        print("overall status: BLOCKED")
        return 1
    print("overall status: REFERENCE-CLEAN / HUMAN REVIEW REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
