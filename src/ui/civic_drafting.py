"""Reusable web presentation routes for transient civic-draft previews.

This module owns form/presentation behavior only. Transport and identity arrive
through an injected request-scoped client factory; platform workflow policy
remains in the canonical API.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from fasthtml.common import (
    A, Button, Div, Form, H2, Input, Label, Option, P, Select, Textarea, Titled,
)
from starlette.requests import Request

from src.documents.template_catalogue import list_templates

# One source of truth for WebApp and Telegram template IDs/titles.
_TEMPLATES = tuple(
    (item.template_id, item.title) for item in list_templates(language="en")
)


def _draft_form(selected_template_id: str = "complaint.general") -> Div:
    allowed_ids = {template_id for template_id, _ in _TEMPLATES}
    if selected_template_id not in allowed_ids:
        selected_template_id = "complaint.general"
    return Div(
        H2("Draft a civic document"),
        P("Choose a format, describe the issue, and generate an editable preview. The preview is not saved or submitted."),
        P(
            "This is server-side deterministic processing, not browser-local processing. The issue "
            "and form details are sent to Janavani's preview API only after you agree below. The "
            "preview is not saved or submitted."
        ),
        P(
            "Remote AI improvement is temporarily disabled for free-text issue narratives and pasted "
            "drafts while Janavani implements a privacy-safe, minimized-input boundary. The "
            "deterministic template preview remains available; this flow will not send the raw "
            "narrative or pasted draft to a remote AI provider."
        ),
        Form(action="/ai-drafting/preview", method="post")(
            Label("Document format", for_="template_id"),
            Select(name="template_id", id="template_id")(
                *(Option(label, value=value, selected=value == selected_template_id) for value, label in _TEMPLATES)
            ),
            Label("Describe the issue or purpose", for_="issue"),
            Textarea(name="issue", id="issue", rows=5, required=True, maxlength=5000, placeholder="Describe the issue in your own words."),
            Label("Existing draft to improve (optional)", for_="existing_draft"),
            Textarea(name="existing_draft", id="existing_draft", rows=5, maxlength=8000, placeholder="Paste your draft here, or leave blank."),
            Label("Subject (optional; generated from your description if blank)", for_="subject"),
            Input(name="subject", id="subject", maxlength=200, placeholder="Document subject"),
            Label("Public authority or jurisdiction (required for RTI and administrative evidence-demand drafts)", for_="jurisdiction"),
            Input(name="jurisdiction", id="jurisdiction", maxlength=300, placeholder="e.g. the issuing municipal authority / department"),
            Label("Existing records requested (RTI; one request per line; maximum 12)", for_="requested_documents"),
            Textarea(name="requested_documents", id="requested_documents", rows=4,
                     maxlength=10000,
                     placeholder="Copies of existing work orders\nCopies of inspection reports, if held",),
            Label("Foundational questions or interrogatories (optional; one per line; maximum 12)", for_="part_i_interrogatories"),
            Textarea(name="part_i_interrogatories", id="part_i_interrogatories", rows=4,
                     maxlength=10000,
                     placeholder="Identify the enabling legal provision\nExplain how the amount was calculated",),
            Label("Requested safeguards or administrative conditions (optional; one per line; maximum 12)", for_="requested_conditions"),
            Textarea(name="requested_conditions", id="requested_conditions", rows=4,
                     maxlength=10000,
                     placeholder="Please provide a point-by-point response\nIdentify any applicable appeal process",),
            Label("Rights or remedies to reserve (optional; one per line; maximum 8; include only if relevant)", for_="remedies_reserved"),
            Textarea(name="remedies_reserved", id="remedies_reserved", rows=3,
                     maxlength=5000,
                     placeholder="I reserve any lawful administrative or statutory remedies available on the facts",),
            Label("Requested response period (optional; verify any binding statutory deadline)", for_="response_period"),
            Input(name="response_period", id="response_period", maxlength=120, placeholder="e.g. 14 days requested, subject to applicable law"),
            Label("Requested date (optional; do not treat as a statutory deadline without verification)", for_="deadline_date"),
            Input(name="deadline_date", id="deadline_date", maxlength=40, placeholder="e.g. 15 November 2026"),
            Div(
                Label(
                    Input(type="checkbox", name="preview_processing_consent", value="yes", required=True),
                    " I agree to send these details to Janavani's preview API for transient server-side processing.",
                ),
                P("Do not continue unless you agree to this processing. The preview is not saved or submitted."),
            ),
            Button("Generate preview", type="submit"),
        ),
        A("Return to Janavani", href="/"),
    )


def register_civic_drafting_routes(
    rt, *, client_factory: Callable[[Request], Any]
) -> None:
    """Register the same template-first drafting journey on an independent web runtime."""

    @rt("/ai-drafting")
    def get_ai_drafting(request: Request):
        requested_template = request.query_params.get("template_id", "complaint.general")
        allowed_ids = {template_id for template_id, _ in _TEMPLATES}
        if requested_template not in allowed_ids:
            requested_template = "complaint.general"
        return Titled("Janavani — Civic Document Drafting", _draft_form(requested_template))

    @rt("/ai-drafting/preview")
    def post_ai_drafting(
        request: Request,
        template_id: str,
        issue: str,
        subject: str = "",
        existing_draft: str = "",
        jurisdiction: str = "",
        requested_documents: str = "",
        part_i_interrogatories: str = "",
        requested_conditions: str = "",
        remedies_reserved: str = "",
        response_period: str = "",
        deadline_date: str = "",
        preview_processing_consent: str = "",
    ):
        consent_given = preview_processing_consent.lower() in {"yes", "true", "1", "on"}
        if not consent_given:
            return Titled(
                "Processing consent required",
                Div(
                    H2("Preview not sent"),
                    P("No request was forwarded to the canonical preview API because processing consent was not provided."),
                    _draft_form(template_id),
                ),
            )
        if not issue.strip():
            return Titled("Describe the issue", Div(H2("Issue required"), P("Describe the issue before generating a preview."), _draft_form()))
        payload = {
            "preview_processing_consent": True,
            "template_id": template_id,
            "issue": issue,
            "subject": subject,
            "existing_draft": existing_draft,
            "jurisdiction": jurisdiction,
            "requested_documents": [line.strip() for line in requested_documents.splitlines() if line.strip()],
            "part_i_interrogatories": [
                line.strip() for line in part_i_interrogatories.splitlines() if line.strip()
            ],
            "requested_conditions": [
                line.strip() for line in requested_conditions.splitlines() if line.strip()
            ],
            "remedies_reserved": [
                line.strip() for line in remedies_reserved.splitlines() if line.strip()
            ],
            "response_period": response_period.strip() or None,
            "deadline_date": deadline_date.strip() or None,
            # Remote AI stays disabled until the shared workflow has a tested
            # privacy-safe, minimized-input boundary for arbitrary citizen narratives.
            "use_ai": False,
            "remote_processing_consent": False,
        }
        try:
            result = client_factory(request).preview_civic_draft(payload)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 422:
                detail = exc.response.json().get("detail", "Check the selected document format and required fields.")
            else:
                detail = "The preview service is temporarily unavailable. Your draft was not reported as saved."
            return Titled("Draft preview unavailable", Div(H2("Could not generate preview"), P(str(detail)), _draft_form()))
        except httpx.HTTPError:
            return Titled("Draft preview unavailable", Div(H2("Service unavailable"), P("Could not reach the preview service. Your draft was not reported as saved."), _draft_form()))

        return Titled(
            "Review civic document draft",
            Div(
                H2("Your draft preview"),
                P(f"Template: {dict(_TEMPLATES).get(result['template_id'], result['template_id'])} · version {result['template_version']}"),
                P(f"AI used: {'Yes' if result['ai_used'] else 'No'} · AI status: {result['ai_status']}"),
                P(result["message"]),
                Label("Edit and review your draft (this preview is not saved)"),
                Textarea(result["draft_body"], name="draft_body", id="draft-preview", rows=20, style="width: 100%;"),
                Button("Copy draft", onclick="navigator.clipboard.writeText(document.getElementById('draft-preview').value)"),
                P("Verify facts, recipient, procedure and any legal references before use. Janavani has not submitted or transmitted this document."),
                A("Draft another document", href="/ai-drafting"),
                A("Return to Janavani", href="/"),
            ),
        )
