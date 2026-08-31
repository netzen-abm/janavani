"""Small framework-neutral entry-point for protected capabilities."""

from .guards import require_capability
from src.identity.context import IdentityContext


def authorize_capability(context: IdentityContext, capability: str) -> IdentityContext:
    """Authorize and return the unchanged context for capability execution."""
    require_capability(context, capability)
    return context
