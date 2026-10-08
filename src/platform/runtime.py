"""Process-local shared runtime composition for access surfaces.

The repository instances and canonical Case capability are shared within one
application process so WebApp routes compose over the same Case boundary.
Durable providers remain selected by the provider-neutral composition layer.
"""
from __future__ import annotations

from src.platform.composition import create_authority_repository, create_case_capability, create_case_repository

CASE_REPOSITORY = create_case_repository()
AUTHORITY_REPOSITORY = create_authority_repository()
CASE_CAPABILITY = create_case_capability(CASE_REPOSITORY)
