"""Contracts for location-to-jurisdiction civic enrichment."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EnrichmentConfidence(str, Enum):
    UNKNOWN = "unknown"
    CANDIDATE = "candidate"
    VERIFIED = "verified"


@dataclass(frozen=True)
class JurisdictionContext:
    district: Optional[str] = None
    local_body: Optional[str] = None
    local_body_type: Optional[str] = None
    constituency: Optional[str] = None
    road_reference: Optional[str] = None
    source_ids: tuple[str, ...] = ()
    confidence: EnrichmentConfidence = EnrichmentConfidence.UNKNOWN
    notes: str = ""
