import os
from fasthtml.common import (
    A, Br, Button, Div, Form, H1, H2, H3, H4, Hidden, Hr, Input, Label, P, Style, Textarea, Titled,
    fast_app,
)
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from src.webapp.identity_gateway import register_identity_gateway_routes, session_secret_for_middleware, validate_web_identity_configuration
from src.webapp.case_list import register_case_list_routes
from src.webapp.csrf_protection import SameOriginCookieMutationMiddleware
from src.webapp.services.api_client import client_for_request
from src.webapp.authority_intake import register_authority_intake_routes

# Initialize the stateless web interface client
app, rt = fast_app(
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
app.add_middleware(SameOriginCookieMutationMiddleware)
app.add_middleware(
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
    """Displays targeted bill details alongside dynamic print and email action controls."""
    return Div(
        Div(
            H2(f"Constitutional Audit Report: {bill_code}"),
            P("This evaluation screens statutory structures against Article 14 (Equality), Article 19 (Freedom), and Article 21 (Liberty)."),
            Hr(),
            Form(action="/dispatch-objection", method="post")(
                Hidden(name="bill_code", value=bill_code),
                H4("Add Your Personal Observations or Local Context (Optional):"),
                Textarea(name="comments", placeholder="Enter your comments here to append them to the formal petition...", rows=3),
                H4("Select Your Official Action Channel:"),
                Label(Input(type="radio", name="format_choice", value="PDF", checked=True), " Download Print-Ready PDF for Official Physical Mail"),
                Label(Input(type="radio", name="format_choice", value="DOCX"), " Download Editable Word Document (.docx) for Local Adjustments"),
                Br(),
                Button("Generate Official Objection Paperwork", type="submit")
            ),
            A("Cancel and Return", href="/"),
            cls="card"
        )
    )

@rt("/dispatch-objection")
def post_dispatch_objection(bill_code: str, comments: str, format_choice: str, request: Request):
    """Triggers document streaming back to the browser based on format preferences."""
    client = client_for_request(request)
    file_bytes = client.download_constitutional_objection(bill_code, comments, format_choice)
    
    if not file_bytes:
        return P("Error generating document stream artifact from backend pools.")
        
    ext = format_choice.lower()
    media = "application/pdf" if format_choice == "PDF" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    from fastapi.responses import Response
    return Response(
        content=file_bytes,
        media_type=media,
        headers={"Content-Disposition": f"attachment; filename=objection_{bill_code}.{ext}"}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.webapp.main:app", host="0.0.0.0", port=8080, reload=True)

