from fasthtml.common import (
    A, Br, Button, Div, Form, H2, H3, H4, Hidden, Hr,
    Input, Label, Link, P, Style, Textarea, Titled, fast_app,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.webapp.ai_drafting import register_ai_drafting_routes
from src.ui.citizen_format_routes import register_citizen_format_routes
from src.webapp.services.api_client import client_for_request
from src.webapp.entry_routes import register_webapp_entry_routes
from src.ui.brand_assets import register_brand_assets

# Initialize the stateless web interface client
app, rt = fast_app(
    hdrs=(
        Style("""
            body { padding: 2rem 0; background-color: #f8f9fa; }
            .container { width: min(100% - 2rem, 960px); margin-inline: auto; }
            .header-banner { text-align: center; margin-bottom: 3rem; }
            .brand-lockup { display: flex; align-items: center; justify-content: center; gap: .75rem; margin-bottom: .75rem; }
            .brand-lockup img { display: block; width: 64px; height: 64px; object-fit: contain; flex: 0 0 64px; }
            .brand-lockup h1 { margin: 0; }
            .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem; }
            .triangle-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; background-color: #ffe6e6; color: #cc0000; }
        """),
        Link(rel="icon", type="image/svg+xml", href="/favicon.svg"),
    )
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

register_webapp_entry_routes(
    rt, client_factory=lambda request: client_for_request(request)
)
register_case_workspace_routes(rt)
register_ai_drafting_routes(rt)
register_citizen_format_routes(rt, client_factory=lambda request: client_for_request(request))
register_brand_assets(rt)


async def protect_user_generated_responses(request: Request, call_next):
    """Prevent browsers and intermediaries from caching citizen-submitted POST responses."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    private_format_page = request.url.path.startswith("/citizen-formats") or (request.url.path == "/ai-drafting" and "format_id" in request.query_params)
    if request.method in {"POST", "PUT", "PATCH"} or private_format_page:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=protect_user_generated_responses)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.webapp.main:app", host="0.0.0.0", port=8080, reload=True)


