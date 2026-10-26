"""Resolve deployment mode consistently at the WebApp trust boundary.

Vercel's platform environment is authoritative for production so an omitted
JANAVANI_RUNTIME_MODE cannot silently disable secure-cookie and OIDC checks.
On Render/local development, the explicit Janavani setting remains the source
of truth. Vercel preview deployments map to test mode.
"""
from __future__ import annotations

import os

_SUPPORTED = frozenset({"development", "test", "production"})


def runtime_mode() -> str:
    platform_mode = os.getenv("VERCEL_ENV", "").strip().lower()
    if platform_mode == "production":
        return "production"

    configured = os.getenv("JANAVANI_RUNTIME_MODE", "").strip().lower()
    if configured:
        if configured not in _SUPPORTED:
            raise RuntimeError("Unsupported JANAVANI_RUNTIME_MODE")
        return configured

    if platform_mode == "preview":
        return "test"
    return "development"


def is_production_runtime() -> bool:
    return runtime_mode() == "production"
