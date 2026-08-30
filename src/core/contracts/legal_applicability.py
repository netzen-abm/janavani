"""Contracts for mapping a citizen's core issue to relevant civic law.

This is a routing layer, not a legal-advice engine. It identifies candidate
legal domains and requires authoritative verification before citizen-facing
claims or documents are generated.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LegalDomain(str, Enum):
    CONSTITUTIONAL = "constitutional"
    RTI = "rti"
    EVIDENCE = "evidence"
    CONSUMER = "consumer"
    CONTRACT = "contract"
    COMPETITION = "competition"
    LOCAL_GOVERNMENT = "local_government"
    PUBLIC_SERVICES = "public_services"
    ENVIRONMENT = "environment"
    LABOUR = "labour"
    WELFARE = "welfare"
    LAND_REVENUE = "land_revenue"
    ELECTRICITY = "electricity"
    TRANSPORT = "transport"
    EDUCATION = "education"
    PUBLIC_HEALTH = "public_health"
    CORRUPTION_ACCOUNTABILITY = "corruption_accountability"
    LEGAL_AID = "legal_aid"
    OTHER_CIVIC = "other_civic"


@dataclass(frozen=True)
class LegalSourceCandidate:
    source_id: str
    title: str
    domain: LegalDomain
    jurisdiction: Optional[str] = None
    verification_required: bool = True
    reason: str = ""


@dataclass(frozen=True)
class LegalApplicabilityResult:
    core_issue: str
    candidates: tuple[LegalSourceCandidate, ...]
    court_research_enabled: bool = False
    authoritative_verification_required: bool = True
