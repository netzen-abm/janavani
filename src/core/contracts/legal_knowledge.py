"""Shared legal knowledge registry contract.

JanaVani uses authoritative, versioned sources rather than relying on model
weights as the sole legal knowledge store. Practical drafting references are
kept separate from primary law and can never silently override it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LegalSourceTier(str, Enum):
    PRIMARY_LAW = "primary_law"
    OFFICIAL_RULE = "official_rule"
    OFFICIAL_NOTIFICATION = "official_notification"
    OFFICIAL_GUIDANCE = "official_guidance"
    VERIFIED_DECISION = "verified_decision"
    PRACTICAL_REFERENCE = "practical_reference"


class LegalKnowledgeStatus(str, Enum):
    VERIFIED = "verified"
    PENDING_REVIEW = "pending_review"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class LegalKnowledgeItem:
    item_id: str
    title: str
    tier: LegalSourceTier
    jurisdiction: str
    source_url: Optional[str] = None
    citation: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    status: LegalKnowledgeStatus = LegalKnowledgeStatus.PENDING_REVIEW
    replaces: Optional[str] = None
    notes: Optional[str] = None
