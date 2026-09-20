"""Canonical shared dependencies for the Web civic-case adapter.

The Web surface is an adapter. Its capabilities are composed once from the
same provider-neutral surface graph used by other access surfaces.
"""
from src.platform.surface_case_composition import create_surface_case_composition

_COMPOSITION = create_surface_case_composition()
CAPABILITY = _COMPOSITION.case_capability
CIVIC_ACTION = _COMPOSITION.civic_action_capability
EVIDENCE = _COMPOSITION.evidence_capability
AUTHORITY = _COMPOSITION.authority_capability
CONSENT = _COMPOSITION.consent_capability
