"""Citizen case-workspace routes; canonical API owns lifecycle and authorization."""
from __future__ import annotations

from uuid import uuid4

from fastapi.responses import Response
from fasthtml.common import A, Button, Div, Form, H2, H3, Input, Label, P, Select, Option, Textarea, Titled
from starlette.requests import Request

from src.webapp.services.api_client import client_for_request


def _sign_in_required():
    """Render a safe response when the request identity is missing."""
    return Titled("Sign-in required", Div(
        H2("Sign-in required"),
        P("Your secure Janavani session is missing or expired. Sign in again before opening a case."),
        A("Return to dashboard", href="/"),
    ))


def register_case_workspace_routes(rt) -> None:
    """Register UI routes that forward each request's verified identity assertion."""

    @rt("/cases/{case_id}/prepare")
    def get_case_workspace(case_id: str, request: Request):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        case = client.get_case(case_id)
        if case.get("status") == "ready":
            refs = case.get("document_refs") or []
            if not refs:
                return Titled("Document unavailable", Div(H2("Document unavailable"), P("No approved document reference exists; no new draft was created."), A("Return to dashboard", href="/")))
            document_id = refs[-1]
            return Titled("Case ready for download", Div(
                H2("Final review confirmed"), P(f"Case {case_id}: ready"),
                P("The approved document is read-only. Download it and send it yourself; Janavani does not transmit submissions."),
                Form(action=f"/cases/{case_id}/artifact", method="post")(
                    Input(type="hidden", name="document_id", value=document_id),
                    Select(name="document_format")(Option("PDF", value="pdf", selected=True), Option("Word document", value="docx")),
                    Button("Download reviewed document"),
                ), A("Return to dashboard", href="/"),
            ))
        draft = client.prepare_document_draft(case_id)
        return Titled(f"Janavani Case {case_id}", Div(
            H2("Janavani Citizen Case Workspace"),
            P(f"Case ID: {case['case_id']}"),
            P(f"Lifecycle status: {case['status']}"),
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
        ))

    @rt("/cases/{case_id}/review")
    def post_case_review(case_id: str, request: Request, subject: str, body: str, reason: str = ""):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        draft = client.prepare_document_draft(case_id)
        client.review_document(case_id, document_id=draft["document_id"], subject=subject, body=body, reason=reason or None)
        result = client.start_review(case_id, subject=subject, narrative=body)
        return Titled("Draft review saved", Div(
            H2("Draft saved for review"),
            P(f"Case {case_id}: {result.get('status', 'review')}"),
            P("Before marking the case ready, confirm that you intend to download the document and submit it yourself. Janavani will not transmit it."),
            Form(action=f"/cases/{case_id}/consent", method="post")(
                Input(type="hidden", name="action_id", value=uuid4().hex),
                Label(
                    Input(type="checkbox", name="explicit_confirmation", value="yes", required=True),
                    " I have reviewed this document and consent to prepare it for my own download and submission.",
                ),
                Button("Record preparation consent"),
            ),
            A("Continue case review", href=f"/cases/{case_id}/prepare"),
        ))

    @rt("/cases/{case_id}/consent")
    def post_case_consent(case_id: str, request: Request, action_id: str = "", explicit_confirmation: str = ""):
        if not action_id.strip() or len(action_id) > 200:
            return Titled("Consent action expired", Div(
                H2("Please review the document again"),
                P("The confirmation identifier is missing or invalid. No consent was recorded."),
                A("Return to document review", href=f"/cases/{case_id}/prepare"),
            ))
        if explicit_confirmation != "yes":
            return Titled("Consent required", Div(
                H2("No consent recorded"),
                P("Tick the explicit confirmation box to record consent."),
                A("Return to document review", href=f"/cases/{case_id}/prepare"),
            ))
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        result = client.record_explicit_consent(case_id, action_id=action_id)
        return Titled("Preparation consent recorded", Div(
            H2("Preparation consent recorded"),
            P(f"Case {case_id}: {result.get('status', 'review')}"),
            P("This records permission to prepare the document; the case is not ready yet. Review the final document and confirm readiness next. Janavani will not transmit it."),
            Form(action=f"/cases/{case_id}/ready", method="post")(
                Label(
                    Input(type="checkbox", name="ready_confirmation", value="yes", required=True),
                    " I have checked the final document and approve it as ready for download.",
                ),
                Button("Confirm final review and mark ready"),
            ),
            A("Return to document review", href=f"/cases/{case_id}/prepare"),
        ))

    @rt("/cases/{case_id}/artifact")
    def post_case_artifact(case_id: str, request: Request, document_format: str = "pdf", document_id: str = ""):
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        if not document_id.strip():
            return Titled("Document unavailable", Div(H2("Document unavailable"), P("No reviewed document was identified. No new draft was created."), A("Return to case workspace", href=f"/cases/{case_id}/prepare")))
        payload = client.generate_artifact(case_id, document_id=document_id, document_format=document_format)
        media_type = "application/pdf" if document_format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return Response(
            content=payload,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="janavani-{case_id}.{document_format}"',
                "Cache-Control": "no-store, private",
            },
        )

    @rt("/cases/{case_id}/ready")
    def post_case_ready(case_id: str, request: Request, ready_confirmation: str = ""):
        if ready_confirmation != "yes":
            return Titled("Final confirmation required", Div(
                H2("Case not marked ready"),
                P("No readiness change was made. Review the final document and tick the confirmation box first."),
                A("Return to document review", href=f"/cases/{case_id}/prepare"),
            ))
        client = client_for_request(request)
        if not client.identity_assertion:
            return _sign_in_required()
        draft = client.prepare_document_draft(case_id)
        result = client.mark_ready(case_id, subject=draft.get("subject"), narrative=draft.get("body"))
        status = result.get("status", "unknown")
        if status != "ready":
            return Titled("Case not ready", Div(
                H2("The case has not reached ready status"),
                P(f"Case {case_id}: {status}"),
                P("No download is offered until the canonical case service confirms readiness."),
                A("Return to case workspace", href=f"/cases/{case_id}/prepare"),
            ))
        return Titled("Case ready for download", Div(
            H2("Final review confirmed"),
            P(f"Case {case_id}: ready"),
            P("The document is ready for download. You must send it yourself; Janavani does not transmit submissions."),
            Form(action=f"/cases/{case_id}/artifact", method="post")(
                Input(type="hidden", name="document_id", value=draft["document_id"]),
                Select(name="document_format")(
                    Option("PDF", value="pdf", selected=True),
                    Option("Word document", value="docx"),
                ),
                Button("Download reviewed document"),
            ),
            A("Open case workspace", href=f"/cases/{case_id}/prepare"),
        ))
