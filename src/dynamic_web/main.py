"""Independent public Dynamic Web presentation for JanaVani.

This is a distinct ASGI runtime from the authenticated WebApp and Telegram
webhook. Presentation, pathway selection and draft form UI have explicit
module boundaries; the canonical API owns identity, drafting policy and data.
"""
from __future__ import annotations

from fasthtml.common import A, Div, H1, H2, H3, Meta, P, Style, Titled, fast_app
from starlette.responses import JSONResponse

from src.adapters.janavani_platform_client import client_for_request
from src.dynamic_web.pathways import pathway_form, register_pathway_routes, site_nav
from src.dynamic_web.styles import DYNAMIC_WEB_STYLES
from src.ui.civic_drafting import register_civic_drafting_routes


app, rt = fast_app(
    hdrs=(
        Style(DYNAMIC_WEB_STYLES),
        Meta(
            name="description",
            content=(
                "JanaVani helps citizens choose civic pathways and prepare editable "
                "documents through reusable templates, with optional consent-gated AI improvement."
            ),
        ),
        Meta(name="theme-color", content="#071d30"),
    )
)


@rt("/")
def get_home():
    """Render the public landing page without requiring the API or Telegram."""
    return Titled(
        "JanaVani — The Infrastructure of Citizen Voice",
        Div(
            site_nav(),
            Div(
                Div(
                    P("THE INFRASTRUCTURE OF CITIZEN VOICE", cls="eyebrow"),
                    H1("WE, THE PEOPLE OF INDIA"),
                    P(
                        "Civic infrastructure for meaningful citizen participation. Understand "
                        "a public issue, choose an appropriate civic pathway, and prepare a "
                        "document you can review and edit.",
                        cls="lead",
                    ),
                    Div(
                        A("Find a civic pathway", href="/pathway", cls="button"),
                        A("Draft a civic document", href="/ai-drafting", cls="button secondary"),
                        cls="actions",
                    ),
                    cls="wrap",
                ),
                cls="hero",
            ),
            Div(
                Div(
                    H2("From citizen concern to informed action"),
                    P(
                        "JanaVani helps make civic procedures easier to navigate. It is not a "
                        "government authority, court, or substitute for qualified legal advice."
                    ),
                    Div(
                        Div(
                            H3("Complaint"),
                            P("Describe a problem and ask the responsible authority to examine it."),
                            cls="card",
                        ),
                        Div(
                            H3("RTI"),
                            P("Request existing records with a clear public authority and record list."),
                            cls="card",
                        ),
                        Div(
                            H3("Representation"),
                            P("Present a position and request lawful administrative consideration."),
                            cls="card",
                        ),
                        cls="grid",
                    ),
                    pathway_form(),
                    cls="wrap",
                ),
                cls="section",
            ),
            Div(
                Div(
                    H2("Designed for citizen control"),
                    P(
                        "Draft previews are sent to the configured JanaVani preview API for "
                        "transient processing and are not saved or submitted by this site. "
                        "Remote AI is optional, requires explicit request-scoped consent, and "
                        "also requires verified identity."
                    ),
                    P(
                        "Review all facts, recipients, statutory references and deadlines before "
                        "use. A polished draft is not proof that its claims are true."
                    ),
                    A("Read the processing boundary", href="/privacy"),
                    cls="wrap intro",
                ),
                cls="section",
            ),
            Div(Div(P("JanaVani · Public Dynamic Web · Independent runtime"), cls="wrap"), cls="footer"),
        ),
    )


@rt("/privacy")
def get_privacy():
    """Explain which processing happens at the public surface and canonical API."""
    return Titled(
        "JanaVani — Processing and Privacy",
        Div(
            site_nav(),
            Div(
                Div(
                    H1("Understand the data boundary"),
                    H2("Pathway selection"),
                    P(
                        "The pathway selector sends a purpose choice to this web service. "
                        "JanaVani does not persist that choice as a citizen profile or case."
                    ),
                    H2("Document preview"),
                    P(
                        "When you request a draft preview, the issue, selected fields and any "
                        "pasted draft are sent to the configured JanaVani preview API for "
                        "transient processing. The preview is not saved or submitted by this site."
                    ),
                    H2("Optional remote AI"),
                    P(
                        "Remote AI must be requested explicitly and requires the applicable "
                        "identity and request-scoped consent checks. Without that authorization, "
                        "deterministic template drafting remains available. Do not include "
                        "unnecessary personal or sensitive details."
                    ),
                    H2("Your control"),
                    P(
                        "Review the draft before use. Verify facts, recipients, the relevant "
                        "disclosure process, statutes and deadlines. JanaVani does not automatically "
                        "submit or email documents."
                    ),
                    A("Return home", href="/"),
                    cls="wrap intro",
                ),
                cls="section",
            ),
        ),
    )


@rt("/liveness")
def get_liveness():
    """Surface health check; does not require the API or messaging service."""
    return JSONResponse({"status": "alive", "surface": "dynamic-web"})


register_pathway_routes(rt)
register_civic_drafting_routes(rt, client_factory=client_for_request)


@app.middleware("http")
async def protect_responses(request, call_next):
    """Keep citizen-entered POST payloads and outputs out of shared caches."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.method in {"POST", "PUT", "PATCH"}:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response
