"""Provider-neutral external identity references."""

from dataclasses import dataclass, field
from typing import FrozenSet, Optional


@dataclass(frozen=True)
class ExternalIdentity:
    """A provider identity mapped to a Janavani principal."""

    provider: str
    subject: str
    principal_id: str
    authentication_method: str
    verified: bool = False
    revoked_at: Optional[str] = None
    scopes: FrozenSet[str] = field(default_factory=frozenset)
    capabilities: FrozenSet[str] = field(default_factory=frozenset)

    def is_active(self) -> bool:
        return self.revoked_at is None

    def is_usable(self) -> bool:
        return self.is_active() and self.verified
