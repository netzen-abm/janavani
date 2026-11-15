"""Enforce the active-source maintainability ceiling.

Historical archives are intentionally excluded. This guard is deterministic and
can run in CI without importing application code.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOTS = ("src", "api", "crates")
EXCLUDED_PARTS = {"archive", "docs", "janavani_v2", "janavani_v3"}
EXTENSIONS = {".py", ".rs"}
DEFAULT_LIMIT = 180

# A narrowly documented exception prevents file size alone from forcing a split
# that would separate consent validation, grant history and Case audit invariants.
DOCUMENTED_OVERRIDES = {
    "src/capabilities/consent.py": (
        "Consent issuance, scope/owner validation, grant versioning and Case audit "
        "attachment form one cohesive consent boundary; do not split only to meet "
        "a line-count target."
    ),
}


def active_files(root: Path):
    for base in ROOTS:
        directory = root / base
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.suffix in EXTENSIONS and not EXCLUDED_PARTS.intersection(path.parts):
                yield path


def violations(root: Path, limit: int) -> list[tuple[str, int]]:
    result = []
    for path in active_files(root):
        lines = len(path.read_text(encoding="utf-8").splitlines())
        relative = str(path.relative_to(root))
        if lines > limit and relative not in DOCUMENTED_OVERRIDES:
            result.append((relative, lines))
    return sorted(result, key=lambda item: item[1], reverse=True)


def documented_overrides(root: Path, limit: int) -> list[tuple[str, int, str]]:
    result = []
    for path in active_files(root):
        relative = str(path.relative_to(root))
        if relative not in DOCUMENTED_OVERRIDES:
            continue
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > limit:
            result.append((relative, lines, DOCUMENTED_OVERRIDES[relative]))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    failures = violations(args.root, args.limit)
    exceptions = documented_overrides(args.root, args.limit)
    if failures:
        print(f"Active source files over {args.limit} lines without a documented boundary exception:")
        for path, lines in failures:
            print(f"{lines:4d} {path}")
        return 1
    if exceptions:
        print("Documented cohesive-boundary exceptions (review; do not split solely by size):")
        for path, lines, reason in exceptions:
            print(f"{lines:4d} {path}: {reason}")
    print(f"Active source files comply with the {args.limit}-line guideline or have a documented exception.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
