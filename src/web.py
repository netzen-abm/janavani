"""Compatibility entry point for the canonical Janavani Web/API runtime.

The canonical application is assembled by ``src.web.canonical_app``.
This module intentionally contains no independent Web runtime, provider access,
or cross-surface process management. It remains as a compatibility import for
older local/deployment references while the repository converges on one Web
runtime authority.
"""
from __future__ import annotations

from src.web.canonical_app import app, create_canonical_app

__all__ = ["app", "create_canonical_app"]
