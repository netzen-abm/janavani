"""HTTP route adapter for reusable civic-draft presentation."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode

import httpx
from fasthtml.common import A, Div, H2, P, Textarea, Button, Label, Titled
from starlette.requests import Request

from src.adapters.janavani_document_format_client import JanavaniDocumentFormatClient
from src.ui.civic_drafting import _TEMPLATES, _draft_form


def register_civic_drafting_routes(rt, *, client_factory: Callable[[Request], Any]) -> None:
    """Register transient drafting routes using the same shared presentation component."""
    allowed_ids = {template_id for template_id, _ in _TEMPLATES}
    labels = dict(_TEMPLATES)

    @rt("/ai-drafting")
    def get_ai_drafting(request: Request):
        requested = request.query_params.get("template_id", "complaint.general")
        if requested not in allowed_ids:
            requested = "complaint.general"
        format_id = request.query_params.get("format_id", "").strip()
        if format_id:
            try:
                saved = JanavaniDocumentFormatClient(client_factory(request)).get_format(format_id)
                if saved["template_id"] not in allowed_ids:
                    raise ValueError("Saved format references an unsupported template")
                requested = str(saved["template_id"])
                notice = P("Using your private saved structure. Only the saved section layout is reused.")
                return Titled("JanaVani — Civic Document Drafting", Div(notice, _draft_form(requested, format_id)))
            except (httpx.HTTPError, RuntimeError, ValueError):
                return Titled(
                    "Saved format unavailable",
                    Div(H2("Could not load this private format"),
                        P("Sign in with the account that owns the format, or choose a catalogue format."),
                        _draft_form(requested), A("View my saved formats", href="/citizen-formats")),
                )
        return Titled("Janavani — Civic Document Drafting", _draft_form(requested))

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
        saved_format_id: str = "",
    ):
        consent = preview_processing_consent.lower() in {"yes", "true", "1", "on"}
        if not consent:
            return Titled(
                "Processing consent required",
                Div(H2("Preview not sent"),
                    P("No request was forwarded to the canonical preview API because processing consent was not provided."),
                    _draft_form(template_id, saved_format_id)),
            )
        if not issue.strip():
            return Titled("Describe the issue", Div(H2("Issue required"),
                P("Describe the issue before generating a preview."), _draft_form(template_id, saved_format_id)))
        payload = {
            "preview_processing_consent": True,
            "template_id": template_id,
            "issue": issue,
            "subject": subject,
            "existing_draft": existing_draft,
            "jurisdiction": jurisdiction,
            "requested_documents": [line.strip() for line in requested_documents.splitlines() if line.strip()],
            "part_i_interrogatories": [line.strip() for line in part_i_interrogatories.splitlines() if line.strip()],
            "requested_conditions": [line.strip() for line in requested_conditions.splitlines() if line.strip()],
            "remedies_reserved": [line.strip() for line in remedies_reserved.splitlines() if line.strip()],
            "response_period": response_period.strip() or None,
            "deadline_date": deadline_date.strip() or None,
            "use_ai": False,
            "remote_processing_consent": False,
        }
        if saved_format_id.strip():
            payload["saved_format_id"] = saved_format_id.strip()
        try:
            result = client_factory(request).preview_civic_draft(payload)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 422:
                detail = exc.response.json().get("detail", "Check the selected document format and required fields.")
            elif exc.response.status_code in {401, 403, 404}:
                detail = "This saved format is unavailable to this account. Sign in as its owner or choose a catalogue format."
            else:
                detail = "The preview service is temporarily unavailable. Your draft was not reported as saved."
            return Titled("Draft preview unavailable",
                Div(H2("Could not generate preview"), P(str(detail)), _draft_form(template_id, saved_format_id)))
        except (httpx.HTTPError, RuntimeError):
            return Titled("Draft preview unavailable",
                Div(H2("Service unavailable"), P("Could not reach the preview service. Your draft was not reported as saved."),
                    _draft_form(template_id, saved_format_id)))

        links = [
            A("Draft another document", href="/ai-drafting"),
            A("View my saved formats", href="/citizen-formats"),
        ]
        if not saved_format_id.strip():
            query = urlencode({"template_id": result["template_id"], "template_version": result["template_version"]})
            links.insert(0, A("Save this reusable structure", href=f"/citizen-formats/confirm?{query}"))
        return Titled(
            "Review civic document draft",
            Div(
                H2("Your draft preview"),
                P(f"Template: {labels.get(result['template_id'], result['template_id'])} · version {result['template_version']}"),
                P(f"AI used: {'Yes' if result['ai_used'] else 'No'} · AI status: {result['ai_status']}"),
                P(result["message"]),
                Label("Edit and review your draft (this preview is not saved)"),
                Textarea(result["draft_body"], name="draft_body", id="draft-preview", rows=20, style="width: 100%;"),
                Button("Copy draft", onclick="navigator.clipboard.writeText(document.getElementById('draft-preview').value)"),
                P("Verify facts, recipient, procedure and any legal references before use. Janavani has not submitted or transmitted this document."),
                *links,
                A("Return to Janavani", href="/"),
            ),
        )
