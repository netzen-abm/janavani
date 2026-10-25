"""Vercel ASGI entrypoint for the independently deployed citizen WebApp."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI


def _repository_root() -> Path:
    """Find the repository root when Vercel bundles this subdirectory."""
    current = Path(__file__).resolve()
    for candidate in (*current.parents, Path.cwd(), Path.cwd().parent):
        if (candidate / "src" / "webapp" / "main.py").is_file():
            return candidate
    raise RuntimeError(
        "Janavani WebApp deployment is missing the shared src/ tree; "
        "enable Vercel source files outside the root directory."
    )


_ROOT = _repository_root()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.webapp.main import app as _webapp  # noqa: E402

# Vercel's Python runtime recognizes a conventional ASGI application here.
# The existing FastHTML app remains the presentation/middleware owner.
app = FastAPI(
    title="Janavani Citizen WebApp",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.mount("/", _webapp)
