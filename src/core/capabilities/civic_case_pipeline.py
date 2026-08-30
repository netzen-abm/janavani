"""Shared orchestration for the first complete civic-case decision path.

This layer composes existing capabilities; channel adapters such as Telegram
and WebApp should call this pipeline instead of implementing their own logic.
It stops at a citizen-confirmable pathway decision and does not submit or send
any document.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.capabilities.authority_discovery import SharedAuthorityDiscovery
from src.core.capabilities.civic_issue_ontology import SharedCivicIssueOntology
from src.core.capabilities.civic_pathway_planner import SharedCivicPathwayPlanner
from src.core.capabilities.jurisdiction_enrichment import SharedJurisdictionEnrichment
from src.core.contracts.authority_discovery import AuthorityCandidate
from src.core.contracts.external_public_data import ExternalDataRecord
from src.core.contracts.jurisdiction_enrichment import JurisdictionContext
from src.core.contracts.civic_issue import CivicIssue
from src.core.contracts.civic_pathway import CivicPathwayDecision, CivicPathway


@dataclass(frozen=True)
class CivicCaseAssessment:
    issue: CivicIssue
    jurisdiction: JurisdictionContext
    authority_candidates: tuple[AuthorityCandidate, ...]
    pathway: CivicPathwayDecision


class SharedCivicCasePipeline:
    """Compose issue, jurisdiction, authority and pathway capabilities."""

    def __init__(
        self,
        *,
        issue_ontology: SharedCivicIssueOntology | None = None,
        jurisdiction_enrichment: SharedJurisdictionEnrichment | None = None,
        authority_discovery: SharedAuthorityDiscovery | None = None,
        pathway_planner: SharedCivicPathwayPlanner | None = None,
    ) -> None:
        self.issue_ontology = issue_ontology or SharedCivicIssueOntology()
        self.jurisdiction_enrichment = jurisdiction_enrichment or SharedJurisdictionEnrichment()
        self.authority_discovery = authority_discovery or SharedAuthorityDiscovery()
        self.pathway_planner = pathway_planner or SharedCivicPathwayPlanner()

    def assess(
        self,
        narrative: str,
        *,
        external_records: tuple[ExternalDataRecord, ...] = (),
        jurisdiction: JurisdictionContext | None = None,
        verified_authority: AuthorityCandidate | None = None,
        procedure_verified: bool = False,
        trigger_id: str | None = None,
    ) -> CivicCaseAssessment:
        issue = self.issue_ontology.classify(narrative)
        context = jurisdiction or self.jurisdiction_enrichment.enrich(external_records)
        candidates = self.authority_discovery.discover(issue, context)
        authority = verified_authority
        if authority is None and len(candidates) == 1:
            authority = candidates[0]
        pathway = self.pathway_planner.plan(
            issue,
            authority,
            procedure_verified=procedure_verified,
            trigger_id=trigger_id,
        )
        return CivicCaseAssessment(issue, context, candidates, pathway)
