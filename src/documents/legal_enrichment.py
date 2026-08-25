"""Optional legal-analysis enrichment for civic documents.

Document composition must not depend on this module. The enrichment result is
analysis metadata, not an authoritative legal determination.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class LegalEnricher(Protocol):
    def enrich(self, issue_text: str) -> Mapping[str, Any] | None:
        """Return optional analysis metadata or None when unavailable."""


class NoOpLegalEnricher:
    """Deterministic fallback that never blocks document composition."""

    def enrich(self, issue_text: str) -> Mapping[str, Any] | None:
        return None


def enrich_document(
    issue_text: str,
    *,
    enricher: LegalEnricher | None = None,
) -> Mapping[str, Any] | None:
    """Run optional legal enrichment without making it a hard dependency."""
    if enricher is None:
        return None
    try:
        return enricher.enrich(issue_text)
    except Exception:
        # Enrichment is explicitly best-effort; the document remains usable.
        return None
