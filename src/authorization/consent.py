"""Explicit consent boundary for consequential Janavani actions."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import FrozenSet

from src.identity.context import IdentityContext


class ConsentRequired(PermissionError):
    """Raised when a consequential action lacks explicit user consent."""


@dataclass(frozen=True)
class ConsentRecord:
    """Immutable record of an explicit consent decision."""

    principal_id: str
    action: str
    consented: bool
    consented_at: datetime


def require_consent(
    context: IdentityContext,
    action: str,
    *,
    consented_actions: FrozenSet[str] = frozenset(),
) -> ConsentRecord:
    """Require an explicit consent grant for a consequential action.

    Consent is intentionally separate from authentication and authorization.
    A caller can be authenticated and authorized yet still be required to
    explicitly approve an external or otherwise consequential action.
    """
    if action not in consented_actions:
        raise ConsentRequired(f"explicit consent required for action: {action}")

    return ConsentRecord(
        principal_id=context.principal.principal_id,
        action=action,
        consented=True,
        consented_at=datetime.now(timezone.utc),
    )
