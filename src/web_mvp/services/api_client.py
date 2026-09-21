"""Thin WebApp adapter for the canonical Janavani Platform API.

The WebApp owns presentation and HTTP transport only. It never supplies a
principal/actor identifier as application data; authenticated identity is
carried only as a verified Bearer assertion.
"""
from __future__ import annotations

import os
from typing import Any

import httpx


class JanavaniWebAPIClient:
    """Call canonical civic-case endpoints without duplicating domain logic."""

    def __init__(self, *, base_url: str | None = None, identity_assertion: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("JANAVANI_WEB_API_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.identity_assertion = identity_assertion or os.getenv("JANAVANI_WEB_IDENTITY_ASSERTION")

    def _headers(self) -> dict[str, str]:
        if not self.identity_assertion:
            raise RuntimeError("Authenticated Web identity is not configured")
        return {"Authorization": f"Bearer {self.identity_assertion}"}

    def create_case(self, *, subject: str, narrative: str, case_type: str = "complaint") -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases",
            json={"case_type": case_type, "subject": subject, "narrative": narrative},
            headers=self._headers(),
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def get_case(self, case_id: str) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/civic/cases/{case_id}",
            headers=self._headers(),
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def prepare_document_draft(self, case_id: str) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/civic/cases/{case_id}/document/draft",
            headers=self._headers(),
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def start_review(self, case_id: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases/{case_id}/review",
            json={},
            headers=self._headers(),
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def add_consent(self, case_id: str, consent_id: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases/{case_id}/consent",
            json={"consent_id": consent_id},
            headers=self._headers(),
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()


    def add_evidence(self, case_id: str, evidence_id: str, *, source_channel: str = "webapp") -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases/{case_id}/evidence",
            json={"evidence_id": evidence_id, "source_channel": source_channel},
            headers=self._headers(), timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def review_document(self, case_id: str, *, document_id: str, subject: str | None = None, body: str | None = None, reason: str | None = None) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases/{case_id}/document/review",
            json={"document_id": document_id, "subject": subject, "body": body, "reason": reason},
            headers=self._headers(), timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def generate_artifact(self, case_id: str, *, document_id: str, document_format: str = "pdf") -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases/{case_id}/document/artifact",
            json={"document_id": document_id, "document_format": document_format},
            headers=self._headers(), timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def mark_ready(self, case_id: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/cases/{case_id}/ready",
            json={}, headers=self._headers(), timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def submit_complaint_draft(self, citizen_input: str) -> dict[str, Any]:
        """Compatibility adapter: create the canonical Case from free-form input."""
        result = self.create_case(subject="Citizen civic issue", narrative=citizen_input)
        return {"case_id": result["case_id"], "status": result["status"]}

    def download_constitutional_objection(
        self, bill_code: str, comments: str, format_choice: str
    ) -> bytes | None:
        """Legacy UI hook retained without reviving the retired dispatch path."""
        del bill_code, comments, format_choice
        return None
