"""WebApp landing and case-creation entry routes.

Keep page entry and the create-case consent boundary together; lifecycle,
review, explicit submission consent and artifact routes remain in
src.webapp.case_workspace. The canonical API remains authoritative for records.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, H3, Img, Input, Label, P, Script, Textarea, Title,
)
from starlette.requests import Request


def register_webapp_entry_routes(
    rt, *, client_factory: Callable[[Request], Any]
) -> None:
    """Register the WebApp home page and explicitly consented case creation."""

    @rt("/local-vault/scope")
    def get_local_vault_scope(request: Request):
        """Proxy the authenticated account namespace without exposing identity data."""
        try:
            return client_factory(request).get_local_vault_scope()
        except (RuntimeError, ValueError):
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Sign-in required"}, status_code=401)
        except Exception:
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Local vault scope unavailable"}, status_code=503)

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
                        "Start a letter, complaint or RTI draft",
                        href="/ai-drafting",
                        style="display: inline-block; margin-top: 1rem;",
                    ),
                    style="text-align: center; margin-bottom: 3rem;",
                ),
                Div(
                    H3("📝 Create a Civic Case"),
                    P(
                        "Your narrative is saved in this browser first. Creating a Case sends "
                        "only minimal lifecycle metadata to the canonical API."
                    ),
                    Form(id="local-case-draft-form", action="/submit-issue", method="post")(
                        Input(type="hidden", name="case_type", value="complaint"),
                        Textarea(
                            name="citizen_input",
                            id="citizen-input",
                            placeholder="Describe the civic issue...",
                            rows=6,
                            required=True,
                            maxlength=20000,
                        ),
                        P(id="local-vault-status", role="status"),
                        Button("Export local draft (JSON)", id="export-local-draft", type="button"),
                        Button("Clear local drafts on this browser", id="clear-local-drafts", type="button"),
                        Button("Create Case", type="submit", cls="button-primary"),
                    ),
                    Script(src="/assets/janavani-local-draft-form.js"),
                    cls="card",
                ),
                cls="container",
            ),
        )

    @rt("/submit-issue")
    def post(
        request: Request,
        local_draft_id: str = "",
        case_type: str = "complaint",
    ):
        """Create only a metadata shell; citizen narrative stays in browser storage."""
        import re
        if not re.fullmatch(r"local-[a-zA-Z0-9-]{8,80}", local_draft_id):
            return Div(
                Div(H3("Local draft required"), P("No Case was created. Save a draft in your browser first."), A("Return", href="/"), cls="card")
            )
        try:
            result = client_factory(request).create_case_shell(case_type=case_type)
        except (RuntimeError, ValueError):
            return Div(Div(H3("Sign-in required"), P("Authenticate before creating a Case shell. Your draft remains in this browser."), A("Return", href="/"), cls="card"))
        except Exception:
            return Div(Div(H3("Case creation unavailable"), P("No Case was created. Your local draft remains in this browser."), A("Return", href="/"), cls="card"))
        if "error" in result:
            return Div(Div(H3("Case creation failed"), P(result["error"]), A("Return", href="/"), cls="card"))
        from starlette.responses import JSONResponse
        return JSONResponse(
            {
                "case_id": result.get("case_id"),
                "status": result.get("status"),
                "content_transmitted": False,
            },
            headers={"Cache-Control": "no-store, private"},
        )
