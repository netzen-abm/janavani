"""Shared, channel-neutral civic issue ontology classifier.

This is deliberately conservative: it produces structured candidate signals,
not legal conclusions. Production deployments can replace the rule classifier
with another implementation behind the same contract.
"""

from __future__ import annotations

import re

from src.core.contracts.civic_issue import CivicIssue, IssueDomain, IssueNeed, IssueSignal


class SharedCivicIssueOntology:
    _patterns: tuple[tuple[IssueDomain, tuple[str, ...]], ...] = (
        (IssueDomain.ROADS, ("road", "pothole", "street", "highway")),
        (IssueDomain.WATER, ("water", "pipeline", "drainage", "leak")),
        (IssueDomain.ELECTRICITY, ("electricity", "power", "transformer", "pole")),
        (IssueDomain.LOCAL_GOVERNMENT, ("panchayat", "municipality", "corporation", "ward")),
        (IssueDomain.EDUCATION, ("school", "college", "teacher", "education")),
        (IssueDomain.HEALTH, ("hospital", "clinic", "health", "medicine")),
        (IssueDomain.WELFARE, ("ration", "pension", "welfare", "benefit")),
        (IssueDomain.LAND_REVENUE, ("land", "survey", "revenue", "property")),
        (IssueDomain.ENVIRONMENT, ("pollution", "waste", "river", "environment")),
        (IssueDomain.TRANSPORT, ("bus", "transport", "traffic", "vehicle")),
        (IssueDomain.CONSUMER, ("consumer", "refund", "product", "service provider")),
        (IssueDomain.RTI_INFORMATION, ("rti", "information", "records", "documents", "file")),
    )

    def classify(self, narrative: str, *, location_hint: str | None = None) -> CivicIssue:
        if not narrative.strip():
            raise ValueError("narrative is required")
        text = narrative.casefold()
        signals: list[IssueSignal] = []
        for domain, words in self._patterns:
            hits = tuple(word for word in words if re.search(r"\b" + re.escape(word) + r"\b", text))
            if hits:
                signals.append(IssueSignal(domain, self._need(text), domain.value, min(1.0, 0.55 + 0.1 * len(hits)), hits))
        if not signals:
            signals.append(IssueSignal(IssueDomain.OTHER, self._need(text), "other", 0.1))
        facts = self._verification_flags(text)
        return CivicIssue(narrative.strip(), tuple(signals), location_hint, facts)

    @staticmethod
    def _need(text: str) -> IssueNeed:
        has_info = any(x in text for x in ("information", "records", "documents", "how much", "rti"))
        has_remedy = any(x in text for x in ("broken", "not working", "delayed", "denied", "repair", "problem", "complaint"))
        if has_info and has_remedy:
            return IssueNeed.MULTIPLE
        if has_info:
            return IssueNeed.INFORMATION
        if any(x in text for x in ("evidence", "proof")):
            return IssueNeed.EVIDENCE
        if any(x in text for x in ("accountability", "responsible", "why")):
            return IssueNeed.ACCOUNTABILITY
        return IssueNeed.REMEDY

    @staticmethod
    def _verification_flags(text: str) -> tuple[str, ...]:
        flags = []
        if any(x in text for x in ("said", "told me", "apparently", "heard")):
            flags.append("reported statement requires verification")
        if any(x in text for x in ("sanctioned", "approved", "order", "rule")):
            flags.append("claimed official decision/rule requires authoritative verification")
        return tuple(flags)
