"""WebApp facade over the canonical platform runtime-mode policy."""
from __future__ import annotations

from src.config.runtime import resolve_runtime_mode


def runtime_mode() -> str:
    """Return the canonical platform-aware runtime mode."""
    return resolve_runtime_mode()


def is_production_runtime() -> bool:
    """True only when the shared runtime policy identifies production."""
    return runtime_mode() == "production"
