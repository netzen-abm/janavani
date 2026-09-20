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
        if lines > limit:
            result.append((str(path.relative_to(root)), lines))
    return sorted(result, key=lambda item: item[1], reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    failures = violations(args.root, args.limit)
    if failures:
        print(f"Active source files over {args.limit} lines:")
        for path, lines in failures:
            print(f"{lines:4d} {path}")
        return 1
    print(f"All active source files are <= {args.limit} lines.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
