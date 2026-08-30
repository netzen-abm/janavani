"""Shared RTI question-quality checks.

The engine improves precision without pretending to determine legal eligibility.
Final procedural/legal checks remain dependent on verified current sources.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RTIQuestionAssessment:
    question: str
    score: int
    issues: tuple[str, ...]
    suggestions: tuple[str, ...]

    @property
    def acceptable(self) -> bool:
        return self.score >= 70 and not any("missing" in item for item in self.issues)


class RTIQuestionQualityEngine:
    """Assess whether a proposed RTI question is concrete and record-oriented."""

    ACTION_WORDS = ("why", "explain", "reason", "take action", "please solve", "why did")
    RECORD_WORDS = ("copy", "record", "order", "file", "register", "report", "minutes", "sanction", "work order", "inspection")

    def assess(self, question: str) -> RTIQuestionAssessment:
        text = " ".join(question.split())
        lower = text.lower()
        issues: list[str] = []
        suggestions: list[str] = []
        score = 100

        if len(text) < 15:
            issues.append("question is too short")
            score -= 35
        if not re.search(r"\b(20\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text):
            issues.append("missing time period or date")
            suggestions.append("Specify the relevant period or date range where possible.")
            score -= 15
        if any(word in lower for word in self.ACTION_WORDS):
            issues.append("question may seek an explanation or remedy rather than identifiable information")
            suggestions.append("Ask for the underlying record, order, file note, report, or other identifiable information instead.")
            score -= 20
        if not any(word in lower for word in self.RECORD_WORDS):
            issues.append("question does not clearly identify a record or information item")
            suggestions.append("Identify the specific record, document, register, order, report, or data requested.")
            score -= 20
        if len(text) > 600:
            issues.append("question may be unnecessarily broad")
            suggestions.append("Split the request into smaller, precise information items.")
            score -= 15

        return RTIQuestionAssessment(text, max(score, 0), tuple(issues), tuple(suggestions))

    def assess_many(self, questions: list[str]) -> tuple[RTIQuestionAssessment, ...]:
        return tuple(self.assess(question) for question in questions)
