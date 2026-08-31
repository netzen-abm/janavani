"""Request context helpers for the shared identity boundary."""

from dataclasses import dataclass
from typing import Optional

from .principal import Principal


@dataclass(frozen=True)
class IdentityContext:
    """Identity context attached to a request after adapter resolution."""

    principal: Principal
    request_id: Optional[str] = None


def anonymous_context(
    principal_id: str,
    *,
    interface: str = "unknown",
    request_id: Optional[str] = None,
) -> IdentityContext:
    """Create a non-authenticated context for capabilities that permit it."""
    return IdentityContext(
        principal=Principal(principal_id=principal_id, interface=interface),
        request_id=request_id,
    )
