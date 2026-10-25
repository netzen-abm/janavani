from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_HELPER = REPOSITORY_ROOT / "src" / "webapp" / "prepare_vercel_bundle.py"
WEBAPP_VERCEL_CONFIG = REPOSITORY_ROOT / "src" / "webapp" / "vercel.json"


def test_vercel_install_command_stages_the_webapp_package_first():
    config = json.loads(WEBAPP_VERCEL_CONFIG.read_text(encoding="utf-8"))

    assert config["installCommand"] == (
        "python prepare_vercel_bundle.py && pip install -r requirements.txt && python verify_vercel_runtime.py"
    )


def test_bundle_staging_is_repeatable_and_excludes_previous_bundle(tmp_path: Path):
    """Exercise the exact nested-root layout without mutating the checkout."""
    repository_root = tmp_path / "repo"
    project_root = repository_root / "src" / "webapp"
    project_root.mkdir(parents=True)
    (project_root / "main.py").write_text("app = object()\n", encoding="utf-8")
    (project_root / "case_workspace.py").write_text(
        "CANONICAL_CASE_MODULE = True\n", encoding="utf-8"
    )
    (project_root / "prepare_vercel_bundle.py").write_text(
        BUNDLE_HELPER.read_text(encoding="utf-8"), encoding="utf-8"
    )

    # Model a stale bundle from a previous install/build. It must be replaced,
    # not recursively copied into the next deployment package.
    stale_package = project_root / "src" / "webapp"
    stale_package.mkdir(parents=True)
    (stale_package / "stale_bundle.py").write_text("STALE = True\n", encoding="utf-8")

    for _ in range(2):
        subprocess.run(
            [sys.executable, str(project_root / "prepare_vercel_bundle.py")],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )

    staged_package = project_root / "src" / "webapp"
    assert (staged_package / "main.py").is_file()
    assert (staged_package / "case_workspace.py").is_file()
    assert (staged_package / "runtime_mode.py").is_file() is False  # fixture only stages its canonical fixture files
    assert not (staged_package / "stale_bundle.py").exists()
    assert not (staged_package / "prepare_vercel_bundle.py").exists()
    assert not (staged_package / "src" / "webapp").exists()
