"""Prepare the WebApp package for its isolated Vercel project root.

The monorepo remains the single source of truth. Vercel deploys this project from
src/webapp, while the application uses canonical src.webapp.* imports. Stage a
deployment-only copy under src/webapp/src/webapp so those imports resolve inside
the function bundle without duplicating maintained source in the repo.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
CANONICAL_WEBAPP = REPOSITORY_ROOT / "src" / "webapp"
BUNDLE_PACKAGE_ROOT = PROJECT_ROOT / "src" / "webapp"


def prepare_bundle() -> None:
    if not (CANONICAL_WEBAPP / "main.py").is_file():
        raise RuntimeError(
            "Cannot stage WebApp bundle: repository-level src/webapp/main.py "
            "is missing. Check Vercel Root Directory and source-files settings."
        )

    # Copy the canonical package into a temporary directory first. Ignore the
    # generated nested bundle so repeat installs are idempotent rather than
    # recursively copying a previous build into itself.
    with tempfile.TemporaryDirectory(prefix="janavani-webapp-bundle-") as temp_dir:
        staged_source = Path(temp_dir) / "webapp"
        shutil.copytree(
            CANONICAL_WEBAPP,
            staged_source,
            ignore=shutil.ignore_patterns(
                "__pycache__", ".pytest_cache", "*.pyc", "tests",
                "test_*.py", "*_test.py", ".git", "src",
                "prepare_vercel_bundle.py", "verify_vercel_runtime.py",
            ),
        )
        if BUNDLE_PACKAGE_ROOT.exists():
            shutil.rmtree(BUNDLE_PACKAGE_ROOT)
        BUNDLE_PACKAGE_ROOT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staged_source, BUNDLE_PACKAGE_ROOT)

    if not (BUNDLE_PACKAGE_ROOT / "main.py").is_file():
        raise RuntimeError("WebApp deployment bundle preparation did not complete.")


if __name__ == "__main__":
    prepare_bundle()
