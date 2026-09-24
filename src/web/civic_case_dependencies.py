"""Canonical WebApp capability graph over the shared civic-action vertical slice."""
from src.web.composition import create_web_civic_action_composition

_COMPOSITION = create_web_civic_action_composition()
CAPABILITY = _COMPOSITION.case_capability
CIVIC_ACTION = _COMPOSITION.civic_action
EVIDENCE = _COMPOSITION.evidence_capability
AUTHORITY = _COMPOSITION.authority_capability
CONSENT = _COMPOSITION.consent_capability
DOCUMENT_REVIEW = _COMPOSITION.document_review_capability
CIVIC_ACTION_VERTICAL_SLICE = _COMPOSITION.civic_action_vertical_slice
