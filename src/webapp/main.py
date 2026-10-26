import sys
from pathlib import Path

# The WebApp is deployed as a subdirectory on some hosts. Resolve the monorepo
# root before importing shared capabilities; never duplicate those modules.
for _candidate in (*Path(__file__).resolve().parents, Path.cwd(), Path.cwd().parent):
    if (_candidate / "src" / "webapp" / "main.py").is_file():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, H3, Input, Label, P, Style, Textarea, Titled,
    fast_app,
)
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from src.webapp.identity_gateway import register_identity_gateway_routes, session_secret_for_middleware
from src.webapp.auth_options import register_auth_options_route
from src.webapp.runtime_mode import is_production_runtime
from src.webapp.case_list import register_case_list_routes
from src.webapp.csrf_protection import SameOriginCookieMutationMiddleware
from src.webapp.services.api_client import client_for_request
from src.webapp.authority_intake import register_authority_intake_routes
from src.webapp.anonymous_intake import register_anonymous_intake_routes

# Initialize the stateless web interface client
webapp, rt = fast_app(
    hdrs=(
        Style("""
            body { padding: 2rem 0; background-color: #f8f9fa; }
            .container { max-width: 900px; }
            .header-banner { text-align: center; margin-bottom: 3rem; }
            .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem; }
            .triangle-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; background-color: #ffe6e6; color: #cc0000; }
        """)
    )
)
webapp.add_middleware(SameOriginCookieMutationMiddleware)
webapp.add_middleware(
    SessionMiddleware,
    secret_key=session_secret_for_middleware(),
    session_cookie="janavani_web_session",
    max_age=1800,
    same_site="lax",
    https_only=is_production_runtime(),
)

@rt("/")
def get(request: Request):
    """Make anonymous document drafting the primary path; identity is optional."""
    authenticated = bool(client_for_request(request).identity_assertion)
    account_link = (
        Form(action="/auth/logout", method="post")(Button("Sign out"))
        if authenticated else A("Optional sign-in for tracking", href="/auth/options")
    )
    return Titled(
        "Janavani — The Infrastructure of Citizen Voice",
        Div(
            Div(
                H1("JANAVANI"),
                H2("Your voice. Your rights. Your next step."),
                P("Narrate what happened in your own words. Janavani can prepare a complaint, an RTI application seeking existing records, or both."),
                style="text-align:center;margin-bottom:2rem;",
            ),
            Div(
                H3("Describe the incident"),
                P("No account is needed to generate a draft. Avoid sharing unnecessary personal or highly sensitive information."),
                Form(action="/draft", method="post")(
                    Textarea(
                        name="narrative",
                        placeholder=(
                            "Example: The streetlights in our lane have not worked for two weeks. "
                            "I want the municipality to repair them and provide copies of complaint and action-taken records."
                        ),
                        rows=8,
                        required=True,
                        maxlength=5000,
                    ),
                    Button("Generate my draft", type="submit", cls="button-primary"),
                ),
                P("Your narrative is processed transiently for this draft and is not saved as a Janavani Case in this no-login flow. Review every fact and placeholder before sending."),
                account_link,
                (
                    A("View my tracked Cases", href="/cases")
                    if authenticated else P(
                        "Want follow-up and cross-device tracking later? "
                        "Review the sign-in options; anonymous drafting remains available."
                    ),
                ),
                cls="card",
            ),
            Div(
                H3("Help build Janavani"),
                P(
                    "Volunteer contributions are welcome in code, automated tests, accessibility, "
                    "Malayalam and other Indian-language support, documentation, and user experience."
                ),
                P(
                    "Generated documents are currently in English; Malayalam and other Indian-language "
                    "document translation are not enabled yet."
                ),
                A(
                    "Volunteer in coding",
                    href="https://github.com/netzen-abm/janavani",
                    target="_blank",
                    rel="noopener noreferrer",
                ),
                P(
                    "Please never post citizen narratives, personal data, credentials, or API keys "
                    "in public issues."
                ),
                cls="card",
            ),
        ),
    )

@rt("/bill-review/{bill_code}")
def get_bill_review(bill_code: str):
    """Fail closed until legislative profiles and authority provenance are verified."""
    del bill_code
    return HTMLResponse(
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Constitutional review unavailable — Janavani</title></head><body><main>"
        "<h1>Constitutional bill review is temporarily unavailable</h1>"
        "<p>Janavani has not yet verified the source provenance for the legislative "
        "profiles required by this workflow. To avoid presenting unverified legal "
        "analysis as authoritative, this document-generation route is disabled.</p>"
        "<p>You can still use the authenticated citizen workspace to create and "
        "continue a regular civic Case.</p>"
        "<p>No constitutional assessment or document has been generated or sent.</p>"
        "<p><a href='/'>Return to the citizen workspace</a></p>"
        "</main></body></html>",
        status_code=503,
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Content-Security-Policy": "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "X-Frame-Options": "DENY",
        },
    )


@rt("/dispatch-objection", methods=["POST"])
def post_dispatch_objection():
    """Reject the retired document path explicitly; never imply generation."""
    return HTMLResponse(
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Document route retired — Janavani</title></head><body><main>"
        "<h1>This document route is not available</h1>"
        "<p>No file was generated and nothing was transmitted. Return to the "
        "citizen workspace to continue a supported civic Case workflow.</p>"
        "<p><a href='/'>Return to Janavani</a></p>"
        "</main></body></html>",
        status_code=410,
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Content-Security-Policy": "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "X-Frame-Options": "DENY",
        },
    )


from src.webapp.case_workspace import register_case_workspace_routes
from src.webapp.identity_pairing_workspace import register_identity_pairing_routes

register_case_workspace_routes(rt)
register_identity_pairing_routes(rt)
register_identity_gateway_routes(rt)
register_auth_options_route(rt)
register_case_list_routes(rt)
register_authority_intake_routes(rt)
register_anonymous_intake_routes(rt)

@rt("/liveness")
def webapp_liveness():
    return P("alive")


# Vercel discovers a conventional top-level assignment. Keep one canonical
# FastHTML ASGI application so route and middleware introspection stays coherent.
app = webapp

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.webapp.main:app", host="0.0.0.0", port=8080, reload=True)

