"""Canonical shared dependencies for the Web civic-case adapter.

Web is a thin access surface. Its capability graph is composed once from the
same provider-neutral infrastructure used by Telegram and other surfaces.
"""
from src.platform.surface_case_composition import create_surface_case_composition

_COMPOSITION = create_surface_case_composition()

CAPABILITY = _COMPOSITION.case_capability
CIVIC_ACTION = _COMPOSITION.civic_action_capability
EVIDENCE = _COMPOSITION.evidence_capability
AUTHORITY = _COMPOSITION.authority_capability
CONSENT = _COMPOSITION.consent_capability
DOCUMENT_REVIEW = _COMPOSITION.document_review_capability
IDENTITY_LINKS = _COMPOSITION.identity_link_repository
