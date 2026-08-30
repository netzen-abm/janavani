"""Channel-neutral authority discovery.

Discovery proposes candidates; verification is a separate gate. This module
never infers legal responsibility solely from geography or AI output.
"""

from __future__ import annotations

from typing import Iterable

from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.civic_issue import CivicIssue, IssueDomain
from src.core.contracts.jurisdiction_enrichment import JurisdictionContext


class SharedAuthorityDiscovery:
    def discover(
        self,
        issue: CivicIssue,
        jurisdiction: JurisdictionContext,
        candidates: Iterable[AuthorityCandidate] = (),
    ) -> tuple[AuthorityCandidate, ...]:
        supplied = tuple(candidates)
        if supplied:
            return supplied

        local = jurisdiction.local_body
        results: list[AuthorityCandidate] = []
        for signal in issue.signals:
            if not local:
                continue
            if signal.domain == IssueDomain.LOCAL_GOVERNMENT:
                results.append(AuthorityCandidate(
                    authority_id=f"local-body:{local}",
                    name=local,
                    authority_type=jurisdiction.local_body_type or "local_body",
                    jurisdiction=jurisdiction.district,
                    reason="local-government issue with matching jurisdiction context",
                ))
            elif signal.domain == IssueDomain.ROADS:
                results.append(AuthorityCandidate(
                    authority_id=f"road-local:{local}",
                    name=local,
                    authority_type="local_body_road_authority_candidate",
                    jurisdiction=jurisdiction.district,
                    reason="road issue with matching local-body context; responsible road agency requires verification",
                ))
        return tuple(results)

    @staticmethod
    def verify(candidate: AuthorityCandidate, *, source_ids: tuple[str, ...]) -> AuthorityCandidate:
        if not source_ids:
            raise ValueError("authoritative source_ids are required for verification")
        return AuthorityCandidate(
            authority_id=candidate.authority_id,
            name=candidate.name,
            authority_type=candidate.authority_type,
            jurisdiction=candidate.jurisdiction,
            reason=candidate.reason,
            source_ids=source_ids,
            status=AuthorityStatus.VERIFIED,
            to_address=candidate.to_address,
            to_email=candidate.to_email,
            cc_address=candidate.cc_address,
            cc_email=candidate.cc_email,
        )
