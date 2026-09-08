"""Legacy document-service boundary.

This module is retained only as migration evidence/compatibility surface.
Canonical civic document generation must flow through the shared
``CivicActionCapability`` so Case ownership, evidence references, authority
verification, consent and lifecycle policy are enforced before an artifact is
produced.

The old API accepts free-form user/office data and therefore cannot establish
those invariants. It is deliberately fail-closed rather than silently creating
a second document-generation path.
"""
from __future__ import annotations


_LEGACY_MIGRATION_MESSAGE = (
    "Legacy document_service is not an authoritative Janavani document path. "
    "Use CivicActionCapability.generate_reviewable_artifact with an owned "
    "canonical Case and verified authority."
)


def generate_complaint_document(*args: object, **kwargs: object) -> str:
    """Reject the retired legacy document API instead of bypassing policy."""
    raise RuntimeError(_LEGACY_MIGRATION_MESSAGE)


def generate_complaint_artifact(*args: object, **kwargs: object) -> object:
    """Reject the retired legacy artifact API instead of bypassing policy."""
    raise RuntimeError(_LEGACY_MIGRATION_MESSAGE)
