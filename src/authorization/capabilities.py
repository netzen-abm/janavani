"""Canonical capability identifiers and public-access policy."""

from typing import FrozenSet

# Public capabilities intentionally remain usable without persistent identity.
PUBLIC_CAPABILITIES: FrozenSet[str] = frozenset(
    {
        "public.search_office",
        "public.complaint_status",
        "citizen.complaint.start",
        "citizen.rating.submit",
    }
)

DOCUMENT_GENERATE = "citizen.document.generate"
DOCUMENT_TRANSMIT = "citizen.document.transmit"

# Consequential capabilities are never public by default.
PROTECTED_CAPABILITIES: FrozenSet[str] = frozenset(
    {DOCUMENT_GENERATE, DOCUMENT_TRANSMIT}
)
