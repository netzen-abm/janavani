import os
from fasthtml.common import (
    A, Button, Div, Form, H1, H3, Input, Label, P, Style, Textarea, Titled,
    fast_app,
)
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from src.webapp.identity_gateway import register_identity_gateway_routes, session_secret_for_middleware, validate_web_identity_configuration
from src.webapp.case_list import register_case_list_routes
from src.webapp.csrf_protection import SameOriginCookieMutationMiddleware
from src.webapp.services.api_client import client_for_request
from src.webapp.authority_intake import register_authority_intake_routes

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
validate_web_identity_configuration()
webapp.add_middleware(SameOriginCookieMutationMiddleware)
webapp.add_middleware(
    SessionMiddleware,
    secret_key=session_secret_for_middleware(),
    session_cookie="janavani_web_session",
    max_age=1800,
    same_site="lax",
    https_only=os.getenv("JANAVANI_RUNTIME_MODE", "development").lower() == "production",
)

@rt("/")
def get(request: Request):
    """Render a truthful workspace with a provider-backed sign-in entry."""
    authenticated = bool(client_for_request(request).identity_assertion)
    if not authenticated:
        return Titled(
            "Janavani — Citizen Action Hub",
            Div(
                H1("JANAVANI"),
                P("Sign in to create a Case, select a verified authority, and continue securely across Janavani surfaces."),
                A("Sign in securely", href="/auth/login"),
            ),
        )
    return Titled(
        "🇮🇳 Janavani — Citizen Action Hub",
        Div(
            Div(
                H1("JANAVANI"),
                P("Create and review a civic Case through the shared Janavani platform."),
                style="text-align: center; margin-bottom: 3rem;",
            ),
            Div(
                Form(action="/auth/logout", method="post")(Button("Sign out")),
                H3("📝 Create a Civic Case"),
                P("Describe the civic issue. The canonical API owns Case, identity, authorization, evidence, consent, document and lifecycle state."),
                Form(action="/submit-issue", method="post")(
                    Label("City", Input(name="city", placeholder="e.g. Kochi", required=True)),
                    Label("Authority type", Input(name="authority_type", placeholder="e.g. district, municipal", required=True)),
                    Textarea(
                        name="citizen_input",
                        placeholder="Describe the civic issue...",
                        rows=6,
                        required=True,
                    ),
                    Button("Create Case", type="submit", cls="button-primary"),
                ),
                A("View my Cases", href="/cases"),
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
register_case_list_routes(rt)
register_authority_intake_routes(rt)

@rt("/liveness")
def webapp_liveness():
    return P("alive")


# Vercel and ASGI hosts need a conventional top-level application instance.
# Keep FastHTML route registration and its middleware cohesive in `webapp`;
# the ASGI wrapper owns only the deployment boundary.
app = FastAPI(
    title="Janavani Citizen WebApp",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.mount("/", webapp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.webapp.main:app", host="0.0.0.0", port=8080, reload=True)

