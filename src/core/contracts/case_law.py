"""Contract for court-judgment references used during civic drafting.

Judgments are optional supporting authorities, never mandatory decorations.
Every citation must be traceable to an authoritative or verified source.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CourtLevel(str, Enum):
    SUPREME_COURT = "supreme_court"
    HIGH_COURT = "high_court"


class PrecedentialWeight(str, Enum):
    BINDING = "binding"
    PERSUASIVE = "persuasive"
    REFERENCE_ONLY = "reference_only"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CaseLawReference:
    case_id: str
    title: str
    court: CourtLevel
    decision_date: Optional[str] = None
    neutral_citation: Optional[str] = None
    citation: Optional[str] = None
    source_url: Optional[str] = None
    legal_issue: str = ""
    proposition: str = ""
    weight: PrecedentialWeight = PrecedentialWeight.UNKNOWN
    verification_status: str = "unverified"


@dataclass(frozen=True)
class CaseLawSearchResult:
    query: str
    references: tuple[CaseLawReference, ...]
    authoritative_search_required: bool = True
