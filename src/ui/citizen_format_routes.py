"""Citizen-facing saved-format pages; source drafts never enter this workflow."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import quote, urlencode

import httpx
from fasthtml.common import A, Button, Div, Form, H2, H3, Input, Label, P, Titled
from starlette.requests import Request

from src.adapters.janavani_document_format_client import JanavaniDocumentFormatClient
from src.documents.template_catalogue import get_template


def _client(request: Request, client_factory: Callable[[Request], Any]) -> JanavaniDocumentFormatClient:
    return JanavaniDocumentFormatClient(client_factory(request))


def _error_page(message: str):
    return Titled("Saved formats", Div(H2("Saved formats are unavailable"), P(message),
        P("Private formats require sign-in and durable storage. No draft text was saved."),
        A("Return to drafting", href="/ai-drafting")))


def register_citizen_format_routes(rt, *, client_factory: Callable[[Request], Any]) -> None:
    """Register consent-separated create/list/delete UI for structural models only."""

    @rt("/citizen-formats")
    def get_list_formats(request: Request):
        try:
            records = _client(request, client_factory).list_formats()
        except httpx.HTTPStatusError as exc:
            message = "Sign in with the account that owns these formats." if exc.response.status_code in {401, 403} else "Durable saved-format storage is not configured yet."
            return _error_page(message)
        except (httpx.HTTPError, RuntimeError):
            return _error_page("Sign in and verify that durable saved-format storage is configured.")
        cards = []
        for record in records:
            title = get_template(record["template_id"], version=record["template_version"]).title
            use_url = "/ai-drafting?" + urlencode({"template_id": record["template_id"], "format_id": record["format_id"]})
            cards.append(Div(
                H3(title), P("Saved structure: " + ", ".join(record["section_field_names"])),
                A("Use this private format", href=use_url),
                Form(action=f"/citizen-formats/{quote(record['format_id'], safe='')}/delete", method="post")(
                    Label(Input(type="checkbox", name="delete_confirmation", value="yes", required=True),
                          " I confirm deletion of this saved format."),
                    Button("Delete saved format", type="submit"),
                ),
            ))
        if not cards:
            cards = [P("No reusable formats have been saved to this account.")]
        return Titled("My saved formats", Div(H2("My private reusable formats"), P(
            "Only structure and canonical template references are saved. Source letters, issue text, personal details and evidence are not stored."),
            *cards, A("Draft a document", href="/ai-drafting")))

    @rt("/citizen-formats/confirm")
    def get_confirm_format_page(request: Request):
        template_id = request.query_params.get("template_id", "complaint.general")
        try:
            version = int(request.query_params.get("template_version", "1"))
            template = get_template(template_id, version=version)
        except (ValueError, LookupError):
            return Titled("Choose a supported format", Div(H2("Unsupported format"),
                P("Choose a format from the canonical catalogue."), A("Draft a document", href="/ai-drafting")))
        required = set(template.required_fields)
        structural_ids = {section.field_name for section in template.sections}
        required_ids = required & structural_ids
        return Titled(
            "Confirm reusable structure",
            Div(
                H2("Save a reusable structure"),
                H3(template.title),
                P("Review the structure below. This saves only selected section identifiers and template version—not this letter, your issue, facts, contact details, evidence, or legal claims."),
                Form(action="/citizen-formats/confirm", method="post")(
                    Input(type="hidden", name="template_id", value=template.template_id),
                    Input(type="hidden", name="template_version", value=str(template.version)),
                    *(Div(Label(Input(type="checkbox", name="section_field_names", value=section.field_name,
                              checked=section.field_name in required_ids), section.heading))
                      for section in template.sections),
                    Div(Label(Input(type="checkbox", name="save_confirmation", value="yes", required=True),
                              " I explicitly confirm saving this private reusable structure.")),
                    Button("Save reusable structure", type="submit"),
                ),
                A("Cancel and return to drafting", href="/ai-drafting"),
            ),
        )

    @rt("/citizen-formats/confirm")
    def post_save_format(request: Request, template_id: str, template_version: int,
                    section_field_names: list[str] | None = None, save_confirmation: str = ""):
        if save_confirmation.lower() not in {"yes", "true", "1", "on"}:
            return Titled("Structure not saved", Div(H2("Separate confirmation required"),
                P("Nothing was saved. Select the confirmation checkbox to save this private structure."),
                A("Return to drafting", href="/ai-drafting")))
        try:
            saved = _client(request, client_factory).save_format(
                template_id=template_id, template_version=template_version,
                section_field_names=section_field_names or [], save_confirmation=True,
            )
        except httpx.HTTPStatusError as exc:
            message = ("Sign in with the account where you want to keep this format." if exc.response.status_code in {401, 403} else "Choose only the listed sections and retain all required sections." if exc.response.status_code == 422 else "Durable saved-format storage is not configured yet.")
            return _error_page(message)
        except (httpx.HTTPError, RuntimeError, ValueError):
            return _error_page("The private format could not be saved. No source draft was stored.")
        use_url = "/ai-drafting?" + urlencode({"template_id": saved["template_id"], "format_id": saved["format_id"]})
        return Titled("Format saved", Div(H2("Private structure saved"),
            P("Only the allow-listed structure was saved. The source draft and personal data were not retained."),
            A("Use this saved format", href=use_url), A("View my saved formats", href="/citizen-formats")))

    @rt("/citizen-formats/{format_id}/delete")
    def post_delete_format(request: Request, format_id: str, delete_confirmation: str = ""):
        if delete_confirmation.lower() not in {"yes", "true", "1", "on"}:
            return Titled("Deletion cancelled", Div(H2("Not deleted"), P("The saved format remains unchanged."),
                A("View my saved formats", href="/citizen-formats")))
        try:
            _client(request, client_factory).delete_format(format_id, delete_confirmation=True)
        except httpx.HTTPStatusError as exc:
            message = "Sign in with the account that owns this format." if exc.response.status_code in {401, 403} else "Saved-format storage is temporarily unavailable."
            return _error_page(message)
        except (httpx.HTTPError, RuntimeError):
            return _error_page("Saved-format storage is temporarily unavailable.")
        return Titled("Format deleted", Div(H2("Saved format deleted"),
            A("View my saved formats", href="/citizen-formats"), A("Draft another document", href="/ai-drafting")))
