"""Compatibility boundary for authority discovery candidates.

The repository contains an older AuthorityReference/confidence candidate shape
and a canonical AuthorityCandidate contract. This adapter provides one explicit
translation boundary without changing either public API in-place.

The canonical contract is authoritative for new code; legacy channel/provider
code should cross this boundary before entering escalation or action planning.
"""
from __future__ import annotations

from typing import Any

from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.case import AuthorityReference, VerificationStatus


def legacy_to_canonical(candidate: Any) -> AuthorityCandidate:
    """Translate a legacy authority candidate into the canonical contract."""
    authority: AuthorityReference = candidate.authority
    status = _status_from_legacy(authority.verification)
    source_id = authority.source if authority.source and authority.source != "system" else ""
    return AuthorityCandidate(
        authority_id=authority.authority_id or f"legacy:{authority.name or 'unknown'}",
        name=authority.name or "Unknown authority",
        authority_type="unknown",
        jurisdiction=authority.location,
        reason=getattr(candidate, "rationale", "legacy authority candidate"),
        source_ids=(source_id,) if source_id else (),
        status=status,
        to_address=None,
        to_email=None,
        cc_address=None,
        cc_email=None,
    )


def canonical_to_legacy(candidate: AuthorityCandidate) -> Any:
    """Translate a canonical candidate for legacy consumers.

    The returned object is deliberately a simple namespace so this adapter does
    not introduce a second domain model into the core contracts.
    """
    from types import SimpleNamespace

    verification = {
        AuthorityStatus.CANDIDATE: VerificationStatus.UNKNOWN,
        AuthorityStatus.VERIFIED: VerificationStatus.VERIFIED,
        AuthorityStatus.STALE: VerificationStatus.REJECTED,
    }[candidate.status]
    authority = AuthorityReference(
        authority_id=candidate.authority_id,
        name=candidate.name,
        location=candidate.jurisdiction,
        source=candidate.source_ids[0] if candidate.source_ids else "system",
        verification=verification,
    )
    return SimpleNamespace(
        authority=authority,
        confidence=1.0 if candidate.status == AuthorityStatus.VERIFIED else 0.0,
        rationale=candidate.reason,
        source="system",
    )


def _status_from_legacy(status: VerificationStatus) -> AuthorityStatus:
    if status == VerificationStatus.VERIFIED:
        return AuthorityStatus.VERIFIED
    if status == VerificationStatus.REJECTED:
        return AuthorityStatus.STALE
    return AuthorityStatus.CANDIDATE
