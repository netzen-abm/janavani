"""Explicit Vercel entrypoint alias for the canonical citizen WebApp ASGI app."""
from __future__ import annotations

import sys
from pathlib import Path

# Vercel can execute this file from the src/webapp root directory. Add the
# repository root so this alias resolves the same canonical module as Render
# and the monorepo runtime. Do not create a second ASGI wrapper here.
_current = Path(__file__).resolve()
for _candidate in (*_current.parents, Path.cwd(), Path.cwd().parent):
    if (_candidate / "src" / "webapp" / "main.py").is_file():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break
else:
    raise RuntimeError("Janavani WebApp deployment cannot locate the shared src/ tree.")

from src.webapp.main import app  # noqa: E402
