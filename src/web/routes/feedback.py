"""Canonical feedback route boundary.

M3-D.2 intentionally re-exports the existing feedback router instead of
rewriting its behavior. This creates the canonical domain import boundary
while preserving the existing public route implementation during migration.
"""

from src.web.feedback_router import router

__all__ = ["router"]
