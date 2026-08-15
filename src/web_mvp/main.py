import os
from fasthtml.common import *
from services.api_client import JanavaniWebAPIClient

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
    """Renders the main layout interface dashboard of the Janavani Web MVP platform."""
    return Titled("🇮🇳 Janavani — Citizen Action Hub",
        Container(
            Div(
                H1("JANAVANI"),
                P("Transform civic grievances into structured legal actions through privacy-first workflows."),
                style="text-align: center; margin-bottom: 3rem;"
            ),
            
            # Form Section for Citizen Plain-Text Issue Entry
            Div(
                H3("📝 Submit Your Civic Grievance or Issue"),
                P("Describe the problem in plain natural language (e.g., Malayalam, Kannada, Assamese, or English). Personal data will be scrubbed locally before submission."),
                Form(action="/submit-issue", method="post")(
                    Textarea(name="citizen_input", placeholder="Type your issue here... (e.g., Broken sewage pipeline in ward 4 causing water logging since 2 weeks.)", rows=5, required=True),
                    Button("Analyze Issue & Draft Document", type="submit", cls="button-primary")
                ),
                cls="card"
            ),
            
            # Featured Legislative Compliance Section
            Div(
                H3("⚖️ Live Legislative Compliance Monitor"),
                P("Tracking bills and amendments against the 'Golden Triangle' (Articles 14, 19, 21) of the Indian Constitution."),
                Div(
                    H4("Kerala Public Spaces Regulatory (Amendment) Bill, 2026"),
                    Span("⚠️ Non-Compliant with Golden Triangle", cls="triangle-badge"),
                    P("Proposes strict licensing checks over public gatherings. Infringes upon basic peaceful assembly rights under Article 19."),
                    A("Review Report & File Formal Objection", href="/bill-review/BILL-2026-KL-04", cls="button secondary")
                , style="border-left: 4px solid #cc0000; padding-left: 1rem; margin-top: 1rem;"),
                cls="card"
            )
        )
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
        
    doc = result.get("document", {})
    facts_list = Ul(*[Li(f) for f in doc.get("factual_points", [])])
    prayers_list = Ul(*[Li(p) for p in doc.get("specific_prayers_or_requests", [])])
    
    return Container(
        Div(
            H2("📄 Generated Legal Framework Draft Summary"),
            P(f"**Tracking ID:** {result.get('tracking_id')} (Valid for 30 minutes in transient memory)"),
            Hr(),
            H4("Subject Heading Line:"),
            P(I(doc.get("subject_line"))),
            H4("Identified Authority:"),
            P(doc.get("suggested_ministry_or_department")),
            H4("Parsed Factual Disclosures:"),
            facts_list,
            H4("Constitutional or Regulatory Foundations:"),
            P(", ".join(doc.get("legal_or_policy_basis", []))),
            H4("Specific Remedial Demands:"),
            prayers_list,
            A("Return to Home Dashboard", href="/", style="margin-top: 2rem; display: inline-block;"),
            cls="card"
        )
    )

@rt("/bill-review/{bill_code}")
def get(bill_code: str):
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
def post(bill_code: str, comments: str, format_choice: str):
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
