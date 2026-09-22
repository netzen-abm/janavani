from fasthtml.common import (
    A, Br, Button, Container, Div, Form, H1, H2, H3, H4, Hidden, Hr,
    I, Label, Link, P, Radio, Span, Style, Textarea, Titled, Ul, Li,
    fast_app,
)
from src.web_mvp.services.api_client import JanavaniWebAPIClient

# Initialize the stateless web interface client
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="https://jsdelivr.net"),
        Style("""
            body { padding: 2rem 0; background-color: #f8f9fa; }
            .container { max-width: 900px; }
            .header-banner { text-align: center; margin-bottom: 3rem; }
            .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem; }
            .triangle-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; background-color: #ffe6e6; color: #cc0000; }
        """)
    )
)

@rt("/")
def get():
    """Render the first-class Janavani WebApp civic Case workspace."""
    return Titled(
        "🇮🇳 Janavani — Citizen Action Hub",
        Container(
            Div(
                H1("JANAVANI"),
                P("Create and review a civic Case through the shared Janavani platform."),
                style="text-align: center; margin-bottom: 3rem;",
            ),
            Div(
                H3("📝 Create a Civic Case"),
                P("Describe the civic issue. The canonical API owns Case, identity, authorization, evidence, consent, document and lifecycle state."),
                Form(action="/submit-issue", method="post")(
                    Textarea(
                        name="citizen_input",
                        placeholder="Describe the civic issue...",
                        rows=6,
                        required=True,
                    ),
                    Button("Create Case", type="submit", cls="button-primary"),
                ),
                cls="card",
            ),
        ),
    )

@rt("/submit-issue")
def post(citizen_input: str):
    """Sends user text to the backend microservice and displays the structured draft fields."""
    client = JanavaniWebAPIClient()
    result = client.submit_complaint_draft(citizen_input)
    
    if "error" in result:
        return Container(
            Div(H3("⚠️ Request Processing Failure"), P(result["error"]), A("Return to Dashboard", href="/"), cls="card")
        )
        
    return Container(
        Div(
            H2("📁 Civic Case Created"),
            P(f"Case ID: {result.get('case_id')}"),
            P(f"Status: {result.get('status')}"),
            P("Continue through the canonical Case lifecycle for evidence, document review, consent and submission."),
            A("Return to Home Dashboard", href="/", style="margin-top: 2rem; display: inline-block;"),
            cls="card",
        )
    )

@rt("/bill-review/{bill_code}")
def get_bill_review(bill_code: str):
    """Displays targeted bill details alongside dynamic print and email action controls."""
    return Container(
        Div(
            H2(f"Constitutional Audit Report: {bill_code}"),
            P("This evaluation screens statutory structures against Article 14 (Equality), Article 19 (Freedom), and Article 21 (Liberty)."),
            Hr(),
            Form(action="/dispatch-objection", method="post")(
                Hidden(name="bill_code", value=bill_code),
                H4("Add Your Personal Observations or Local Context (Optional):"),
                Textarea(name="comments", placeholder="Enter your comments here to append them to the formal petition...", rows=3),
                H4("Select Your Official Action Channel:"),
                Label(Radio(name="format_choice", value="PDF", checked=True), " Download Print-Ready PDF for Official Physical Mail"),
                Label(Radio(name="format_choice", value="DOCX"), " Download Editable Word Document (.docx) for Local Adjustments"),
                Br(),
                Button("Generate Official Objection Paperwork", type="submit")
            ),
            A("Cancel and Return", href="/"),
            cls="card"
        )
    )

@rt("/dispatch-objection")
def post_dispatch_objection(bill_code: str, comments: str, format_choice: str):
    """Triggers document streaming back to the browser based on format preferences."""
    client = JanavaniWebAPIClient()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
