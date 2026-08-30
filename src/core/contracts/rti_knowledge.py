"""Contracts for a versioned, source-backed RTI knowledge layer."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class KnowledgeAuthority(str, Enum):
    PRIMARY_LAW = "primary_law"
    OFFICIAL_RULE = "official_rule"
    OFFICIAL_GUIDANCE = "official_guidance"
    VERIFIED_CASE_LAW = "verified_case_law"
    PRACTICAL_GUIDE = "practical_guide"


@dataclass(frozen=True)
class RTIKnowledgeSource:
    source_id: str
    title: str
    authority: KnowledgeAuthority
    jurisdiction: str
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    source_url: Optional[str] = None
    citation: Optional[str] = None
    verified: bool = False


@dataclass(frozen=True)
class RTIKnowledgeFact:
    fact_id: str
    statement: str
    source_id: str
    section: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    verified: bool = False


class RTIKnowledgeRegistry:
    """In-memory contract; persistent implementation can be added later."""

    def __init__(self, sources: tuple[RTIKnowledgeSource, ...] = (), facts: tuple[RTIKnowledgeFact, ...] = ()):
        self.sources = sources
        self.facts = facts

    def verified_sources(self) -> tuple[RTIKnowledgeSource, ...]:
        return tuple(source for source in self.sources if source.verified)

    def verified_facts(self) -> tuple[RTIKnowledgeFact, ...]:
        return tuple(fact for fact in self.facts if fact.verified)
