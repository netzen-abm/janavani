#!/usr/bin/env python3
"""Audit root requirements against Python imports and declared runtime files.

This is intentionally a static audit. It reports dependencies that have no
matching import in tracked Python source, while allowing explicit future or
legacy entries to remain visible for human review.
"""

from __future__ import annotations

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
PACKAGE_TO_IMPORT = {
    "Flask": "flask",
    "FastAPI": "fastapi",
    "uvicorn": "uvicorn",
    "python-dotenv": "dotenv",
    "supabase": "supabase",
    "python-telegram-bot": "telegram",
    "requests": "requests",
    "pandas": "pandas",
    "numpy": "numpy",
    "weasyprint": "weasyprint",
    "reportlab": "reportlab",
    "web3": "web3",
    "ipfshttpclient": "ipfshttpclient",
}


def requirement_names() -> list[str]:
    names: list[str] = []
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)", line)
        if match:
            names.append(match.group(1))
    return names


def imported_modules() -> set[str]:
    modules: set[str] = set()
    for path in ROOT.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            print(f"PARSE_ERROR {path}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module.split(".")[0])
    return modules


def main() -> int:
    imports = imported_modules()
    print("JANAVANI REQUIREMENTS STATIC IMPORT AUDIT")
    print("=" * 48)
    print(f"Python source imports discovered: {len(imports)}")

    for package in requirement_names():
        module = PACKAGE_TO_IMPORT.get(package)
        if module is None:
            print(f"UNMAPPED {package}")
            continue
        status = "USED" if module in imports else "NO_IMPORT_FOUND"
        print(f"{status:16} {package:20} <- {module}")

    print("\nNOTE: NO_IMPORT_FOUND is a review signal, not automatic proof that a dependency is removable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
