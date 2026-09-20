"""Public compatibility surface for the canonical Civic Case capability.

Implementation is split into focused modules; imports from this path remain stable.
"""
from src.capabilities.civic_case_contract import CivicCaseCreateRequest, CivicCaseResult
from src.capabilities.civic_case_impl import CivicCaseCapability

__all__ = ["CivicCaseCapability", "CivicCaseCreateRequest", "CivicCaseResult"]
