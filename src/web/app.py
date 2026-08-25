"""Compatibility entry point for the Janavani web application.

The canonical FastAPI assembly lives in ``src.web.canonical_app``.
This module remains as a compatibility import for deployment configurations
or callers that still reference ``src.web.app:app``.

Do not add business logic or routers here. New routes belong in their domain
router modules and are assembled by ``canonical_app.py``.
"""

from src.web.canonical_app import app, create_canonical_app

__all__ = ["app", "create_canonical_app"]
