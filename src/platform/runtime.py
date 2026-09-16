"""Process-local shared runtime composition for access surfaces.

Repository instances are shared within one application process so access-surface
adapters compose over the same canonical Case/Authority/Evidence boundaries.
Durable providers remain selected by the provider-neutral composition layer.
"""
from __future__ import annotations

from src.platform.composition import (
    create_authority_repository,
    create_case_repository,
    create_development_evidence_repository,
)

CASE_REPOSITORY = create_case_repository()
AUTHORITY_REPOSITORY = create_authority_repository()
EVIDENCE_REPOSITORY = create_development_evidence_repository()
