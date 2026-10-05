"""Public compatibility surface for the canonical Civic Case capability.

Implementation is split into focused modules; imports from this path remain stable.
"""
from src.capabilities.civic_case_contract import CAPABILITY_ID, CivicCaseCreateRequest, CivicCaseResult
from src.capabilities.civic_case_impl import CivicCaseCapability

__all__ = ["CAPABILITY_ID", "CivicCaseCapability", "CivicCaseCreateRequest", "CivicCaseResult"]
