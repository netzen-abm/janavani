"""Reusable web presentation routes for transient civic-draft previews.

This module owns form/presentation behavior only. Transport and identity arrive
through an injected request-scoped client factory; platform workflow policy
remains in the canonical API.
"""
from __future__ import annotations


from fasthtml.common import (
    A, Button, Div, Form, H2, Input, Label, Option, P, Select, Textarea, Titled,
)

from src.documents.template_catalogue import list_templates

# One source of truth for WebApp and Telegram template IDs/titles.
_TEMPLATES = tuple(
    (item.template_id, item.title) for item in list_templates(language="en")
)


def _draft_form(selected_template_id: str = "complaint.general", saved_format_id: str = "") -> Div:
    allowed_ids = {template_id for template_id, _ in _TEMPLATES}
    if selected_template_id not in allowed_ids:
        selected_template_id = "complaint.general"
    template_control = (
        Input(type="hidden", name="template_id", value=selected_template_id)
        if saved_format_id else
        Select(name="template_id", id="template_id")(
            *(Option(label, value=value, selected=value == selected_template_id) for value, label in _TEMPLATES)
        )
    )
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
            Input(type="hidden", name="saved_format_id", value=saved_format_id),
            Label("Saved document structure" if saved_format_id else "Document format", for_="template_id"),
            template_control,
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
        A("View my saved formats", href="/citizen-formats"),
        A("Return to Janavani", href="/"),
    )
