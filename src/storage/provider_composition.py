"""Canonical provider composition for shared Janavani infrastructure.

Surfaces must not independently choose persistence providers.  This module
owns the provider-selection policy at the shared infrastructure boundary.
It deliberately does not instantiate database clients or perform migration.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


# These are the persisted domain boundaries currently recognized by the
# platform.  Decision-only capabilities are intentionally absent.
PERSISTED_DOMAINS = (
    "civic_case",
    "consent",
    "evidence",
    "document_artifact",
    "document_review",
    "authority",
    "policy",
    "submission",
    "accountability_feedback",
    "external_channel",
    "external_identity_links",
)

DEFAULT_PROVIDER = "memory"


class ProviderCompositionError(ValueError):
    """Raised when the shared provider composition is invalid."""


@dataclass(frozen=True)
class ProviderComposition:
    """Immutable provider plan shared by all access surfaces.

    The composition is a policy/configuration object, not a database adapter.
    Each domain may have its own adapter implementation, but the selected
    provider is resolved once at the shared composition boundary.
    """

    providers: Mapping[str, str]

    def __post_init__(self) -> None:
        normalized = {
            domain: provider.strip().lower()
            for domain, provider in self.providers.items()
        }
        unknown = set(normalized) - set(PERSISTED_DOMAINS)
        if unknown:
            raise ProviderCompositionError(
                "Unknown persisted domains: " + ", ".join(sorted(unknown))
            )
        invalid = {
            domain: provider
            for domain, provider in normalized.items()
            if not provider
        }
        if invalid:
            raise ProviderCompositionError(
                "Provider cannot be empty for: " + ", ".join(sorted(invalid))
            )
        object.__setattr__(self, "providers", normalized)

    @classmethod
    def memory_first(cls) -> "ProviderComposition":
        """Return the safe development composition with memory everywhere."""
        return cls({domain: DEFAULT_PROVIDER for domain in PERSISTED_DOMAINS})

    @classmethod
    def from_environment(cls) -> "ProviderComposition":
        """Resolve the shared provider plan without importing any adapter."""
        providers = {
            domain: os.getenv(
                f"JANAVANI_{domain.upper()}_REPOSITORY_PROVIDER", DEFAULT_PROVIDER
            )
            for domain in PERSISTED_DOMAINS
        }
        return cls(providers)

    def provider_for(self, domain: str) -> str:
        """Return the selected provider for one persisted domain."""
        if domain not in PERSISTED_DOMAINS:
            raise ProviderCompositionError(f"Unknown persisted domain: {domain}")
        return self.providers.get(domain, DEFAULT_PROVIDER)

    def with_provider(self, domain: str, provider: str) -> "ProviderComposition":
        """Return a new composition with one domain changed."""
        if domain not in PERSISTED_DOMAINS:
            raise ProviderCompositionError(f"Unknown persisted domain: {domain}")
        updated = dict(self.providers)
        updated[domain] = provider
        return ProviderComposition(updated)
