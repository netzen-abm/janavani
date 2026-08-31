"""Authorization policy evaluation for normalized Janavani identity contexts."""

from dataclasses import dataclass
from typing import FrozenSet

from src.identity.context import IdentityContext


@dataclass(frozen=True)
class AuthorizationPolicy:
    """Policy describing capabilities that anonymous callers may use."""

    anonymous_capabilities: FrozenSet[str] = frozenset()

    def permits(self, context: IdentityContext, capability: str) -> bool:
        if context.principal.has_capability(capability):
            return True
        if context.principal.is_authenticated():
            return capability in context.principal.capabilities
        return capability in self.anonymous_capabilities
