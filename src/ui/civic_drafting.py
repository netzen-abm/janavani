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
            "Your text is sent to Janavani's preview API for transient processing; the local-template "
            "option does not call the AI provider. Reusable starter questions and record requests are "
            "editable in the final preview."
        ),

        Form(action="/ai-drafting/preview", method="post")(
            Label("Document format"),
            Select(name="template_id")(
                *(Option(label, value=value, selected=value == selected_template_id) for value, label in _TEMPLATES)
            ),
            Label("Describe the issue or purpose"),
            Textarea(name="issue", rows=5, required=True, maxlength=5000, placeholder="Describe the issue in your own words."),
            Label("Existing draft to improve (optional)"),
            Textarea(name="existing_draft", rows=5, maxlength=8000, placeholder="Paste your draft here, or leave blank."),
            Label("Subject (optional; generated from your description if blank)"),
            Input(name="subject", maxlength=200, placeholder="Document subject"),
            Label("Public authority or jurisdiction (required for RTI and administrative evidence-demand drafts)"),
            Input(name="jurisdiction", maxlength=300, placeholder="e.g. the issuing municipal authority / department"),
            Label("Existing records requested (RTI; one request per line)"),
            Textarea(name="requested_documents", rows=4, placeholder="Copies of existing work orders\nCopies of inspection reports, if held"),
            Div(
                Label(Input(type="checkbox", name="use_ai", value="yes"), " Improve wording with AI (optional)"),
                P("AI is optional. Without it, Janavani uses the selected reusable template."),
            ),
            Div(
                Label(
                    Input(type="checkbox", name="remote_processing_consent", value="yes"),
                    " I consent to send the issue and any pasted draft to the configured remote AI provider for wording suggestions.",
                ),
                P("Only select this when you understand the provider's processing terms. Legal citations, deadlines, authorities, and evidence are not generated as verified facts."),
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
        use_ai: str = "",
        remote_processing_consent: str = "",
    ):
        if not issue.strip():
            return Titled("Describe the issue", Div(H2("Issue required"), P("Describe the issue before generating a preview."), _draft_form()))
        payload = {
            "template_id": template_id,
            "issue": issue,
            "subject": subject,
            "existing_draft": existing_draft,
            "jurisdiction": jurisdiction,
            "requested_documents": [line.strip() for line in requested_documents.splitlines() if line.strip()],
            "use_ai": use_ai.lower() in {"yes", "true", "1", "on"},
            "remote_processing_consent": remote_processing_consent.lower() in {"yes", "true", "1", "on"},
        }
        if payload["use_ai"] and payload["remote_processing_consent"]:
            origin = request.headers.get("origin")
            host = request.headers.get("host", "").lower()
            from urllib.parse import urlsplit
            if not origin or urlsplit(origin).netloc.lower() != host:
                payload["remote_processing_consent"] = False
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
