"""Citizen case-workspace routes; canonical API owns lifecycle and authorization."""
from __future__ import annotations
import re
from fastapi import HTTPException
from fastapi.responses import Response
from fasthtml.common import A, Button, Div, Form, H2, H3, Input, Label, Li, Option, P, Select, Textarea, Titled, Ul
from starlette.requests import Request
from src.webapp.api_errors import PlatformAPIContractError, safe_api_errors
from src.webapp.services.api_client import client_for_request
def _sign_in_required():
    """Render a safe, user-facing response when no request identity is present."""
    return Titled(
        "Sign-in required",
        Div(
            H2("Sign-in required"),
            P("Your secure Janavani session is missing or expired. Sign in again before opening a case."),
            A("Return to dashboard", href="/"),
        ),
    )
def register_case_workspace_routes(rt) -> None:
    """Register UI routes that forward each request's verified identity assertion."""

    @rt("/cases/{case_id}/prepare")
    @safe_api_errors("open the Case workspace")
    def get_case_workspace(case_id: str, request: Request):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        case = client.get_case(case_id)
        draft = client.prepare_document_draft(case_id)
        events = case.get("events", [])
        event_items = [
            Li(f"{event.get('occurred_at', 'Time unavailable')} — {event.get('event_type', 'Case update')}")
            for event in events
        ]
        return Titled(
            f"Janavani Case {case_id}",
            Div(
                H2("Janavani Citizen Case Workspace"),
                P(f"Case ID: {case['case_id']}"),
                P(f"Lifecycle status: {case['status']}"),
                H3("Case activity"),
                Ul(*event_items) if event_items else P("No lifecycle events recorded yet."),
                P(f"Evidence references: {len(case.get('evidence_refs', []))}; document references: {len(case.get('document_refs', []))}."),
                H3("Review your document"),
                P(draft.get("subject", "Document draft")),
                P(draft.get("body", "")),
                Form(action=f"/cases/{case_id}/review", method="post")(
                    Label("Document subject"),
                    Textarea(draft.get("subject", ""), name="subject", required=True, rows=2),
                    Label("Document body"),
                    Textarea(draft.get("body", ""), name="body", required=True, rows=10),
                    Label("Reason for changes (optional)"),
                    Textarea(name="reason", rows=2),
                    Button("Save reviewed draft", type="submit"),
                ),
                A("Return to dashboard", href="/"),
            ),
        )
    @rt("/cases/{case_id}/review")
    @safe_api_errors("save the reviewed document")
    def post_case_review(case_id: str, request: Request, subject: str, body: str, reason: str = ""):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        draft = client.prepare_document_draft(case_id)
        reviewed = client.review_document(
            case_id,
            document_id=draft["document_id"],
            subject=subject,
            body=body,
            reason=reason or None,
        )
        if reviewed.get("document_id") != draft.get("document_id"):
            raise PlatformAPIContractError("Platform API did not confirm the reviewed document")
        result = client.start_review(case_id, subject=subject, narrative=body)
        return Titled(
            "Draft review saved",
            Div(
                H2("Draft saved for review"),
                P(f"Case {case_id}: {result.get('status', 'review')}"),
                P("Before marking this case ready, confirm that you intend to download the document and submit it yourself. Janavani will not transmit it."),
                Form(action=f"/cases/{case_id}/consent", method="post")(
                    Label(
                        Input(type="checkbox", name="explicit_confirmation", value="yes", required=True),
                        " I have reviewed this document and consent to prepare it for my own download and submission.",
                    ),
                    Button("Confirm consent and mark case ready"),
                ),
                A("Continue case review", href=f"/cases/{case_id}/prepare"),
            ),
        )
    @rt("/cases/{case_id}/consent")
    @safe_api_errors("record explicit consent")
    def post_case_consent(case_id: str, request: Request, explicit_confirmation: str = ""):
        if explicit_confirmation != "yes":
            return Titled(
                "Consent required",
                Div(
                    H2("No consent recorded"),
                    P("Tick the explicit confirmation box to record consent."),
                    A("Return to document review", href=f"/cases/{case_id}/prepare"),
                ),
            )
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        result = client.record_explicit_consent(case_id)
        if result.get("consent_recorded") is not True or result.get("scope") != "citizen_download_and_self_send":
            raise PlatformAPIContractError("Platform API did not confirm the requested consent scope")
        return Titled(
            "Consent recorded",
            Div(
                H2("Explicit consent recorded"),
                P(f"Case {case_id}: {result.get('status', 'ready')}"),
                P("No document has been transmitted. You remain responsible for reviewing and sending it."),
                Form(action=f"/cases/{case_id}/artifact", method="post")(
                    Select(name="document_format")(
                        Option("PDF", value="pdf", selected=True),
                        Option("Word document", value="docx"),
                    ),
                    Button("Download reviewed document"),
                ),
                A("Return to case workspace", href=f"/cases/{case_id}/prepare"),
            ),
        )
    @rt("/cases/{case_id}/artifact")
    @safe_api_errors("download the reviewed document")
    def post_case_artifact(case_id: str, request: Request, document_format: str = "pdf"):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        # Form fields and route parameters are untrusted; the API still owns Case authorization.
        formats = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        normalized_format = document_format.strip().lower()
        media_type = formats.get(normalized_format)
        if media_type is None:
            raise HTTPException(status_code=422, detail="Unsupported document format")
        safe_case_id = re.sub(r"[^A-Za-z0-9_-]", "_", case_id)[:80] or "case"
        draft = client.prepare_document_draft(case_id)
        payload = client.generate_artifact(
            case_id, document_id=draft["document_id"], document_format=normalized_format
        )
        if not payload:
            raise PlatformAPIContractError("Platform API returned an empty document artifact")
        return Response(
            content=payload,
            media_type=media_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="janavani-{safe_case_id}.{normalized_format}"'
                ),
                "Cache-Control": "no-store, private",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
            },
        )
    @rt("/cases/{case_id}/ready")
    @safe_api_errors("mark the Case ready")
    def post_case_ready(case_id: str, request: Request):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        draft = client.prepare_document_draft(case_id)
        result = client.mark_ready(
            case_id, subject=draft.get("subject"), narrative=draft.get("body")
        )
        return Titled(
            "Case ready",
            Div(
                H2("Case lifecycle updated"),
                P(f"Case {case_id}: {result.get('status', 'ready')}"),
                P("Download the document and send it yourself. Janavani does not transmit submissions."),
                A("Open case workspace", href=f"/cases/{case_id}/prepare"),
            ),
        )
