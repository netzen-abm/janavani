"""Canonical shared dependencies for the Web civic-case adapter."""
from src.platform.composition import create_authority_repository, create_case_repository, create_development_evidence_repository
from src.web.composition import create_web_civic_action_composition

_REPOSITORY = create_case_repository()
_EVIDENCE_REPOSITORY = create_development_evidence_repository()
_COMPOSITION = create_web_civic_action_composition(
    case_repository=_REPOSITORY,
    authority_repository=create_authority_repository(),
    evidence_repository=_EVIDENCE_REPOSITORY,
)
CAPABILITY = _COMPOSITION.case_capability
CIVIC_ACTION = _COMPOSITION.civic_action
