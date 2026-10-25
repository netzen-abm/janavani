"""Vercel entrypoint for the independently deployed citizen WebApp."""
from __future__ import annotations

import sys
from pathlib import Path


def _repository_root() -> Path:
    """Find the repository root when Vercel bundles this subdirectory."""
    current = Path(__file__).resolve()
    candidates = [*current.parents, Path.cwd(), Path.cwd().parent]
    for candidate in candidates:
        if (candidate / "src" / "webapp" / "main.py").is_file():
            return candidate
    raise RuntimeError(
        "Janavani WebApp deployment is missing the shared src/ tree; "
        "enable Vercel source files outside the root directory."
    )


_ROOT = _repository_root()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.webapp.main import app  # noqa: E402
