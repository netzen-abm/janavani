"""Janavani shared identity boundary.

Identity is deliberately separate from conversation/workflow state.
"""

from .adapter import DefaultIdentityAdapter, IdentityAdapter
from .external import ExternalIdentity
from .principal import Principal, IdentityMode, AuthenticationMethod

__all__ = [
    "AuthenticationMethod",
    "DefaultIdentityAdapter",
    "ExternalIdentity",
    "IdentityAdapter",
    "IdentityMode",
    "Principal",
]
