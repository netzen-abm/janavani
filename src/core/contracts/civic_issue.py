"""Shared civic issue ontology for natural-language citizen problems."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class IssueDomain(str, Enum):
    LOCAL_GOVERNMENT = "local_government"
    ROADS = "roads"
    WATER = "water"
    ELECTRICITY = "electricity"
    EDUCATION = "education"
    HEALTH = "health"
    WELFARE = "welfare"
    LAND_REVENUE = "land_revenue"
    ENVIRONMENT = "environment"
    CONSUMER = "consumer"
    TRANSPORT = "transport"
    RTI_INFORMATION = "rti_information"
    OTHER = "other"


class IssueNeed(str, Enum):
    REMEDY = "remedy"
    INFORMATION = "information"
    ACCOUNTABILITY = "accountability"
    EVIDENCE = "evidence"
    MULTIPLE = "multiple"


@dataclass(frozen=True)
class IssueSignal:
    domain: IssueDomain
    need: IssueNeed
    label: str
    confidence: float
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class CivicIssue:
    summary: str
    signals: tuple[IssueSignal, ...]
    location_hint: Optional[str] = None
    facts_requiring_verification: tuple[str, ...] = ()
    privacy_redactions_applied: bool = True
    metadata: dict[str, str] = field(default_factory=dict)
