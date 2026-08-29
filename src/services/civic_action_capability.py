"""Canonical orchestration boundary for the first WebApp vertical slice.

This is deliberately provider-neutral: authority, evidence, documents, AI,
and future decentralized providers remain replaceable capabilities.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from src.domain.authority import AuthorityQuery
from src.domain.case import CaseCreate, CaseRecord
from src.services.authority_capability import AuthorityCapability
from src.services.evidence_capability import EvidenceCapability, EvidenceItem
from src.services.case_service import CaseService


class CivicActionContext(BaseModel):
    case: CaseRecord
    authorities: list[Any] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class CivicActionCapability:
    """Builds a reviewable action context without performing external submission."""

    def __init__(self, case_service: CaseService | None = None,
                 authority: AuthorityCapability | None = None,
                 evidence: EvidenceCapability | None = None) -> None:
        self.cases = case_service or CaseService()
        self.authority = authority or AuthorityCapability()
        self.evidence = evidence or EvidenceCapability()

    def create(self, payload: CaseCreate, evidence_items: list[EvidenceItem] | None = None) -> CivicActionContext:
        case = self.cases.create_case(payload)
        matches = self.authority.resolve(AuthorityQuery(issue=case.description, location=case.location))
        registered: list[EvidenceItem] = []
        for item in evidence_items or []:
            if item.case_id != case.id:
                item.case_id = case.id
            result = self.evidence.register(item)
            if result.ok and result.item:
                registered.append(result.item)
        return CivicActionContext(case=case, authorities=matches, evidence=registered)
