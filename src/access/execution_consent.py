"""Execution-context-aware consent enforcement."""
from __future__ import annotations

from dataclasses import dataclass

from src.access.consent import ConsentRepositoryReader, ConsentRequiredError, ConsentRequirement, require_consent
from src.core.execution import CapabilityExecutionContext


@dataclass(frozen=True)
class ExecutionConsentRequirement:
    """Consent requirement bound to the canonical capability execution context."""

    requirement: ConsentRequirement


def require_execution_consent(
    repository: ConsentRepositoryReader,
    requirement: ExecutionConsentRequirement,
    execution_context: CapabilityExecutionContext,
) -> None:
    """Require consent while fail-closing on execution identity and operation scope."""
    context_identity = execution_context.identity.principal.principal_id
    if context_identity != requirement.requirement.subject_id:
        raise ConsentRequiredError("consent subject does not match execution identity")

    require_consent(repository, requirement.requirement)
