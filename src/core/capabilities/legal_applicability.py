"""Shared civic legal-domain routing.

This intentionally performs lightweight candidate routing only. It does not
claim that a statute applies. A verified legal/public-source provider must
confirm applicability before a citizen-facing document relies on it.
"""

from __future__ import annotations

from src.core.contracts.legal_applicability import (
    LegalApplicabilityResult,
    LegalDomain,
    LegalSourceCandidate,
)


class SharedLegalApplicability:
    _RULES: tuple[tuple[tuple[str, ...], LegalDomain, str], ...] = (
        (("rti", "information", "records", "file", "documents"), LegalDomain.RTI, "Possible government-information need."),
        (("road", "drain", "street", "panchayat", "municipality", "water", "garbage"), LegalDomain.LOCAL_GOVERNMENT, "Possible local/public service matter."),
        (("electricity", "power", "connection", "meter"), LegalDomain.ELECTRICITY, "Possible electricity/public-utility matter."),
        (("consumer", "refund", "warranty", "defective", "service"), LegalDomain.CONSUMER, "Possible consumer/service dispute."),
        (("contract", "agreement", "breach", "payment"), LegalDomain.CONTRACT, "Possible contractual matter."),
        (("competition", "cartel", "dominant", "monopoly", "anti-competitive"), LegalDomain.COMPETITION, "Possible competition matter."),
        (("evidence", "record", "photo", "video", "digital"), LegalDomain.EVIDENCE, "Possible evidence-preservation relevance."),
        (("pollution", "waste", "environment", "forest", "water body"), LegalDomain.ENVIRONMENT, "Possible environmental matter."),
        (("salary", "wage", "worker", "employment", "labour"), LegalDomain.LABOUR, "Possible labour/employment matter."),
        (("land", "property", "survey", "revenue", "title"), LegalDomain.LAND_REVENUE, "Possible land/revenue matter."),
        (("school", "college", "education", "teacher"), LegalDomain.EDUCATION, "Possible education matter."),
        (("hospital", "health", "clinic", "medicine"), LegalDomain.PUBLIC_HEALTH, "Possible public-health matter."),
        (("scheme", "pension", "ration", "welfare", "benefit"), LegalDomain.WELFARE, "Possible welfare/public-benefit matter."),
        (("bribe", "corruption", "misconduct", "accountability"), LegalDomain.CORRUPTION_ACCOUNTABILITY, "Possible accountability/corruption matter."),
    )

    def identify(self, core_issue: str, *, jurisdiction: str | None = None) -> LegalApplicabilityResult:
        text = core_issue.lower()
        found: list[LegalSourceCandidate] = []
        seen: set[LegalDomain] = set()
        for keywords, domain, reason in self._RULES:
            if domain in seen:
                continue
            if any(keyword in text for keyword in keywords):
                seen.add(domain)
                found.append(LegalSourceCandidate(
                    source_id=f"candidate:{domain.value}",
                    title=f"Relevant {domain.value.replace('_', ' ')} law/procedure",
                    domain=domain,
                    jurisdiction=jurisdiction,
                    reason=reason,
                ))
        if not found:
            found.append(LegalSourceCandidate(
                source_id="candidate:other_civic",
                title="Other applicable civic law/procedure",
                domain=LegalDomain.OTHER_CIVIC,
                jurisdiction=jurisdiction,
                reason="No specific civic domain was confidently identified; authoritative verification is required.",
            ))
        return LegalApplicabilityResult(core_issue.strip(), tuple(found))
