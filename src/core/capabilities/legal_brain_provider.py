"""Legacy legal knowledge adapter for the shared LegalSourceProvider boundary.

This adapter intentionally does NOT expose the legacy engine's default Article
14 fallback. An unmatched issue is returned as an empty result, because absence
of a verified source must never be converted into an asserted legal basis.

The entries in the legacy knowledge table are treated as knowledge records, not
as automatically verified current law. They therefore remain UNVERIFIED until
an independent source-verification process marks them verified.
"""

from __future__ import annotations

from typing import Iterable

from src.core.contracts.legal_source import LegalSourceReference, SourceVerificationStatus
from src.legal_brain import LEGAL_DATABASE


class LegacyLegalBrainProvider:
    """Expose legacy entries without inheriting unsafe fallback behavior."""

    def search(self, query: str, *, jurisdiction: str | None = None) -> Iterable[LegalSourceReference]:
        normalized = query.lower().replace(" ", "_")
        for key, record in LEGAL_DATABASE.items():
            if key in normalized:
                yield LegalSourceReference(
                    source_id=f"legacy:{key}",
                    title=record["law"],
                    citation=record["section"],
                    jurisdiction=jurisdiction,
                    verification=SourceVerificationStatus.UNVERIFIED,
                    provider="legacy_legal_brain",
                )
