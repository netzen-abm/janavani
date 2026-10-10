"""Citizen case-workspace routes; canonical API owns lifecycle and authorization."""
from __future__ import annotations

from fastapi.responses import Response
from fasthtml.common import A, Button, Container, Form, H2, H3, Input, Label, P, Select, Option, Textarea, Titled
from starlette.requests import Request

from src.webapp.services.api_client import client_for_request


def register_case_workspace_routes(rt) -> None:
    """Register UI routes that forward each request's verified identity assertion."""

    @rt("/cases/{case_id}/prepare")
    def get_case_workspace(case_id: str, request: Request):
        client = client_for_request(request)
        case = client.get_case(case_id)
        draft = client.prepare_document_draft(case_id)
        return Titled(
            f"Janavani Case {case_id}",
            Container(
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
            ),
        )

    @rt("/cases/{case_id}/review")
    def post_case_review(case_id: str, request: Request, subject: str, body: str, reason: str = ""):
        client = client_for_request(request)
        draft = client.prepare_document_draft(case_id)
        reviewed = client.review_document(
            case_id,
            document_id=draft["document_id"],
            subject=subject,
            body=body,
            reason=reason or None,
        )
        result = client.start_review(case_id, subject=subject, narrative=body)
        return Titled(
            "Draft review saved",
            Container(
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
    def post_case_consent(case_id: str, request: Request, explicit_confirmation: str = ""):
        if explicit_confirmation != "yes":
            return Titled(
                "Consent required",
                Container(
                    H2("No consent recorded"),
                    P("Tick the explicit confirmation box to record consent."),
                    A("Return to document review", href=f"/cases/{case_id}/prepare"),
                ),
            )
        client = client_for_request(request)
        result = client.record_explicit_consent(case_id)
        return Titled(
            "Consent recorded",
            Container(
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
    def post_case_artifact(case_id: str, request: Request, document_format: str = "pdf"):
        client = client_for_request(request)
        draft = client.prepare_document_draft(case_id)
        payload = client.generate_artifact(
            case_id, document_id=draft["document_id"], document_format=document_format
        )
        media_type = (
            "application/pdf" if document_format == "pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        return Response(
            content=payload,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="janavani-{case_id}.{document_format}"',
                "Cache-Control": "no-store, private",
            },
        )

    @rt("/cases/{case_id}/ready")
    def post_case_ready(case_id: str, request: Request):
        client = client_for_request(request)
        draft = client.prepare_document_draft(case_id)
        result = client.mark_ready(
            case_id, subject=draft.get("subject"), narrative=draft.get("body")
        )
        return Titled(
            "Case ready",
            Container(
                H2("Case lifecycle updated"),
                P(f"Case {case_id}: {result.get('status', 'ready')}"),
                P("Download the document and send it yourself. Janavani does not transmit submissions."),
                A("Open case workspace", href=f"/cases/{case_id}/prepare"),
            ),
        )
