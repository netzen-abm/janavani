"""WebApp landing and case-creation entry routes.

Keep page entry and the create-case consent boundary together; lifecycle,
review, explicit submission consent and artifact routes remain in
src.webapp.case_workspace. The canonical API remains authoritative for records.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, H3, Img, Input, Label, P, Textarea, Title,
)
from starlette.requests import Request


def register_webapp_entry_routes(
    rt, *, client_factory: Callable[[Request], Any]
) -> None:
    """Register the WebApp home page and explicitly consented case creation."""

    @rt("/")
    def get_home():
        """Render the case-workspace entry point."""
        return (
            Title("🇮🇳 Janavani — Citizen Action Hub"),
            Div(
                Div(
                    Div(
                        Img(
                            src="/brand-assets/brand/janavani-mark",
                            alt="",
                            width="64",
                            height="64",
                        ),
                        H1("JANAVANI"),
                        cls="brand-lockup",
                    ),
                    P(
                        "Create and review a civic case through the shared "
                        "JanaVani platform."
                    ),
                    A(
                        "AI-assisted civic document drafting",
                        href="/ai-drafting",
                        style="display: inline-block; margin-top: 1rem;",
                    ),
                    style="text-align: center; margin-bottom: 3rem;",
                ),
                Div(
                    H3("📝 Create a Civic Case"),
                    P(
                        "Describe the civic issue. The canonical API owns case, "
                        "identity, authorization, evidence, consent, document "
                        "and lifecycle state."
                    ),
                    Form(action="/submit-issue", method="post")(
                        Textarea(
                            name="citizen_input",
                            placeholder="Describe the civic issue...",
                            rows=6,
                            required=True,
                            maxlength=5000,
                        ),
                        Div(
                            Label(
                                Input(
                                    type="checkbox",
                                    name="case_processing_consent",
                                    value="yes",
                                    required=True,
                                ),
                                " I agree to send these details to JanaVani's API "
                                "to create a case record.",
                            ),
                            P(
                                "This creates a JanaVani case record; it is not "
                                "a saved draft preview and does not file anything "
                                "with a government authority. Separate consent "
                                "is required before any later external submission."
                            ),
                        ),
                        Button("Create Case", type="submit", cls="button-primary"),
                    ),
                    cls="card",
                ),
                cls="container",
            ),
        )

    @rt("/submit-issue")
    def post(
        citizen_input: str,
        request: Request,
        case_processing_consent: str = "",
    ):
        """Fail closed before any API call if case-processing consent is absent."""
        consent_given = case_processing_consent.strip().lower() in {
            "yes", "true", "1", "on"
        }
        if not consent_given:
            return Div(
                Div(
                    H3("Consent required"),
                    P("No case was created and no issue details were sent to the API."),
                    A("Return to dashboard", href="/"),
                    cls="card",
                )
            )
        if not citizen_input.strip():
            return Div(
                Div(
                    H3("Issue description required"),
                    P("Describe the civic issue before creating a case."),
                    A("Return to dashboard", href="/"),
                    cls="card",
                )
            )

        try:
            result = client_factory(request).submit_complaint_draft(citizen_input)
        except (RuntimeError, ValueError):
            return Div(
                Div(
                    H3("Sign-in required"),
                    P(
                        "Authenticate through the JanaVani identity gateway "
                        "before creating a case."
                    ),
                    A("Return to dashboard", href="/"),
                    cls="card",
                )
            )

        if "error" in result:
            return Div(
                Div(
                    H3("⚠️ Request Processing Failure"),
                    P(result["error"]),
                    A("Return to dashboard", href="/"),
                    cls="card",
                )
            )

        return Div(
            Div(
                H2("📁 JanaVani Case Created"),
                P(f"Case ID: {result.get('case_id')}"),
                P(f"Status: {result.get('status')}"),
                P(
                    "This creates a JanaVani case record only. Continue through "
                    "the case workspace to review a document and manage any later "
                    "consent. No government filing was performed."
                ),
                Form(action=f"/cases/{result.get('case_id')}/prepare", method="get")(
                    Button("Open Case Workspace", type="submit"),
                ),
                A("Return to home dashboard", href="/"),
                cls="card",
            )
        )
