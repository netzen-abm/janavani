"""Shared planner translating verified issue facts into civic pathways."""

from __future__ import annotations

from src.core.contracts.civic_issue import CivicIssue
from src.core.contracts.civic_pathway import CivicPathway, CivicPathwayDecision
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.capabilities.civic_action_planner import ActionKind


class SharedCivicPathwayPlanner:
    def plan(
        self,
        issue: CivicIssue,
        authority: AuthorityCandidate | None,
        *,
        procedure_verified: bool,
        trigger_id: str | None = None,
    ) -> CivicPathwayDecision:
        if not procedure_verified:
            return CivicPathwayDecision(
                CivicPathway.NEEDS_INFORMATION,
                "Applicable procedure must be verified before selecting a civic pathway.",
                authority_id=authority.authority_id if authority else None,
            )
        if authority is None or authority.status != AuthorityStatus.VERIFIED:
            return CivicPathwayDecision(
                CivicPathway.NEEDS_INFORMATION,
                "A responsible authority must be verified before document preparation.",
            )
        needs = {signal.need.value for signal in issue.signals}
        if "multiple" in needs or ({"remedy", "information"} <= needs):
            pathway = CivicPathway.COMPLAINT_AND_RTI
        elif "information" in needs:
            pathway = CivicPathway.RTI
        elif "remedy" in needs:
            pathway = CivicPathway.COMPLAINT
        else:
            pathway = CivicPathway.NO_ACTION
        return CivicPathwayDecision(
            pathway,
            "Pathway selected from structured issue needs after authority and procedure verification.",
            trigger_id=trigger_id,
            authority_id=authority.authority_id,
            requires_user_confirmation=True,
        )
