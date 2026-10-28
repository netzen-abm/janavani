"""Independent public Dynamic Web presentation for JanaVani.

This is a distinct ASGI runtime from the authenticated WebApp and Telegram
webhook. It reuses the existing template-first drafting routes and catalogue;
it does not own document composition, AI policy, identity, Case persistence,
or submission.
"""
from __future__ import annotations

from urllib.parse import quote

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, H3, Label, Meta, Option, P, Select, Style, Titled, fast_app,
)
from starlette.responses import JSONResponse

from src.adapters.janavani_platform_client import client_for_request
from src.documents.template_catalogue import get_template
from src.ui.civic_drafting import register_civic_drafting_routes


_STYLE = r"""
:root{color-scheme:light;--navy:#071d30;--blue:#184966;--gold:#d6a34a;--paper:#f5f2e9;--ink:#172d3c;--muted:#5c6d78;--line:rgba(23,45,60,.16)}
*{box-sizing:border-box}
body{margin:0;background:#fffdf8;color:var(--ink);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--blue);text-underline-offset:.18em}
a:focus-visible,button:focus-visible,select:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.site-header{background:var(--navy);color:#fff;padding:14px 22px}
.header-inner,.wrap{width:min(1120px,calc(100% - 36px));margin:0 auto}
.header-inner{display:flex;align-items:center;justify-content:space-between;gap:24px}
.brand{font-weight:800;letter-spacing:.08em;color:#fff;text-decoration:none}
.nav{display:flex;gap:18px;flex-wrap:wrap}
.nav a{color:#fff;font-size:.9rem}
main{min-height:70vh}
.hero{background:var(--navy);color:#fff;padding:clamp(54px,9vw,108px) 0}
.eyebrow{margin:0 0 14px;color:#ead3a1;font-size:.75rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
h1,h2,h3{line-height:1.12;letter-spacing:-.035em}
h1{max-width:850px;font-size:clamp(2.5rem,7vw,5.7rem);margin:0 0 22px}
h2{font-size:clamp(1.7rem,4vw,2.8rem)}
.lead{max-width:760px;color:rgba(255,255,255,.84);font-size:clamp(1.05rem,2vw,1.25rem)}
.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.button,button{
 display:inline-block;border:1px solid var(--gold);border-radius:8px;
 background:var(--gold);color:#172d3c;padding:11px 16px;
 font:inherit;font-weight:750;text-decoration:none;cursor:pointer
}
.button.secondary{background:transparent;color:#fff;border-color:rgba(255,255,255,.45)}
.section{padding:clamp(45px,7vw,78px) 0}
.intro{max-width:780px}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:24px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px}
.card p{color:var(--muted)}
.pathway-box{margin-top:28px;padding:clamp(20px,4vw,32px);background:var(--paper);border:1px solid var(--line);border-radius:14px}
label{display:block;font-weight:700;margin:14px 0 7px}
select{width:100%;max-width:620px;padding:12px;border:1px solid #778793;border-radius:7px;background:#fff;font:inherit}
.hint{font-size:.9rem;color:var(--muted)}
footer{background:#edf0f0;padding:28px 0;color:#485b68;font-size:.9rem}
@media(max-width:760px){.header-inner{align-items:flex-start;flex-direction:column}.grid{grid-template-columns:1fr}.nav{gap:12px}.hero{padding:54px 0}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
"""


# These are pathway choices, not a second template catalogue or an AI classifier.
# The display title/version and actual document structure come from the canonical catalogue.
_PATHWAYS = {
    "report_issue": {
        "template_id": "complaint.general",
        "label": "Report a civic issue",
        "guidance": "Use a complaint when you want the responsible authority to examine a specific problem or take action.",
    },
    "public_service": {
        "template_id": "grievance.service",
        "label": "Raise a public-service grievance",
        "guidance": "Use a grievance when a public service is missing, delayed, or not being delivered as expected.",
    },
    "existing_records": {
        "template_id": "rti.records",
        "label": "Request existing public records (RTI)",
        "guidance": "Use RTI to request identifiable existing records. A request for a newly written explanation or a corrective remedy may need a separate representation or grievance.",
    },
    "challenge_notice": {
        "template_id": "administrative.evidence-demand",
        "label": "Question a fee, levy, or administrative notice",
        "guidance": "Request the legal authority, calculation, jurisdiction, supporting records and safeguards. This template does not establish that the fee is invalid.",
    },
    "representation": {
        "template_id": "representation.general",
        "label": "Make a formal representation",
        "guidance": "Use a representation to present facts and request consideration, clarification, or a lawful administrative decision.",
    },
    "petition": {
        "template_id": "petition.general",
        "label": "Prepare a petition",
        "guidance": "Use a petition for a collective or formal request. Verify the proper recipient and required process before circulation or submission.",
    },
}


def _nav():
    return Div(
        Div(
            A("JANAVANI", href="/", cls="brand"),
            Div(
                A("Explore pathways", href="/pathway"),
                A("Draft a document", href="/ai-drafting"),
                A("Privacy", href="/privacy"),
                cls="nav",
            ),
            cls="header-inner",
        ),
        cls="site-header",
    )


def _pathway_form() -> Div:
    return Div(
        H2("Find a civic pathway"),
        P("Choose the task you need to complete. This guided selector is deterministic; it does not classify or store your personal story."),
        Form(action="/pathway", method="post")(
            Label("What are you trying to do?"),
            Select(name="purpose", required=True)(
                Option("Choose a pathway", value="", selected=True),
                *(Option(path["label"], value=key) for key, path in _PATHWAYS.items()),
            ),
            Div(
                Button("Show my pathway"),
                P("This selector sends only your pathway choice. Do not enter names, case numbers, addresses or private narratives here.", cls="hint"),
            ),
        ),
        cls="pathway-box",
    )


app, rt = fast_app(
    hdrs=(
        Style(_STYLE),
        Meta(name="description", content="JanaVani helps citizens choose civic pathways and prepare editable documents through reusable templates, with optional consent-gated AI improvement."),
        Meta(name="theme-color", content="#071d30"),
    )
)


@rt("/")
def get_home():
    return Titled(
        "JanaVani — The Infrastructure of Citizen Voice",
        Div(
            _nav(),
            Div(
                Div(
                    P("THE INFRASTRUCTURE OF CITIZEN VOICE", cls="eyebrow"),
                    H1("WE, THE PEOPLE OF INDIA"),
                    P(
                        "Civic infrastructure for meaningful citizen participation. Understand a public "
                        "issue, choose an appropriate civic pathway, and prepare a document you can "
                        "review and edit.",
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
                    P("JanaVani helps make civic procedures easier to navigate. It is not a government authority, court, or substitute for qualified legal advice."),
                    Div(
                        Div(H3("Complaint"), P("Describe a problem and ask the responsible authority to examine it."), cls="card"),
                        Div(H3("RTI"), P("Request existing records with a clear public authority and record list."), cls="card"),
                        Div(H3("Representation"), P("Present a position and request lawful administrative consideration."), cls="card"),
                        cls="grid",
                    ),
                    _pathway_form(),
                    cls="wrap",
                ),
                cls="section",
            ),
            Div(
                Div(
                    H2("Designed for citizen control"),
                    P(
                        "Draft previews are sent to the configured JanaVani preview API for transient "
                        "processing and are not saved or submitted by this site. Remote AI is optional, "
                        "requires explicit request-scoped consent, and also requires verified identity."
                    ),
                    P("Review all facts, recipients, statutory references and deadlines before use. A polished draft is not proof that its claims are true."),
                    A("Read the processing boundary", href="/privacy"),
                    cls="wrap intro",
                ),
                cls="section",
            ),
            Div(Div(P("JanaVani · Public Dynamic Web · Independent runtime"), cls="wrap"), cls="footer"),
        ),
    )


@rt("/pathway")
def get_pathway():
    return Titled(
        "JanaVani — Choose a Civic Pathway",
        Div(_nav(), Div(Div(H1("Choose your civic task"), _pathway_form(), cls="wrap"), cls="section")),
    )


@rt("/pathway")
def post_pathway(purpose: str):
    pathway = _PATHWAYS.get(purpose)
    if pathway is None:
        return Titled(
            "Choose a supported civic pathway",
            Div(_nav(), Div(Div(H1("Choose a pathway"), P("Select one of the listed tasks to continue."), _pathway_form(), cls="wrap"), cls="section")),
        )
    template = get_template(pathway["template_id"])
    draft_url = f"/ai-drafting?template_id={quote(template.template_id, safe='')}"
    return Titled(
        f"JanaVani — {pathway['label']}",
        Div(
            _nav(),
            Div(
                Div(
                    P("YOUR SELECTED PATHWAY", cls="eyebrow"),
                    H1(pathway["label"]),
                    P(pathway["guidance"], cls="lead"),
                    Div(
                        Div(H3("Suggested reusable format"), P(template.title), cls="card"),
                        Div(H3("Before drafting"), P("Confirm the competent authority, facts, available records, applicable procedure and any binding deadline."), cls="card"),
                        cls="grid",
                    ),
                    Div(
                        A("Continue to this document format", href=draft_url, cls="button"),
                        A("Choose another pathway", href="/pathway", cls="button secondary"),
                        cls="actions",
                    ),
                    P("This is procedural guidance, not a legal determination. The generated document remains editable and is never automatically submitted.", cls="hint"),
                    cls="wrap",
                ),
                cls="section",
            ),
        ),
    )


@rt("/privacy")
def get_privacy():
    return Titled(
        "JanaVani — Processing and Privacy",
        Div(
            _nav(),
            Div(
                Div(
                    H1("Understand the data boundary"),
                    H2("Pathway selection"),
                    P("The pathway selector sends a purpose choice to this web service. JanaVani does not persist that choice as a citizen profile or case."),
                    H2("Document preview"),
                    P(
                        "When you request a draft preview, the issue, selected fields and any pasted "
                        "draft are sent to the configured JanaVani preview API for transient processing. "
                        "The preview is not saved or submitted by this site."
                    ),
                    H2("Optional remote AI"),
                    P(
                        "Remote AI must be requested explicitly and requires the applicable identity "
                        "and request-scoped consent checks. Without that authorization, deterministic "
                        "template drafting remains available. Do not include unnecessary personal or "
                        "sensitive details."
                    ),
                    H2("Your control"),
                    P("Review the draft before use. Verify facts, recipients, the relevant disclosure process, statutes and deadlines. JanaVani does not automatically submit or email documents."),
                    A("Return home", href="/"),
                    cls="wrap intro",
                ),
                cls="section",
            ),
        ),
    )


@rt("/liveness")
def get_liveness():
    return JSONResponse({"status": "alive", "surface": "dynamic-web"})


# Reuse the shared drafting UI and canonical API client without depending on WebApp runtime.
register_civic_drafting_routes(rt, client_factory=client_for_request)


@app.middleware("http")
async def protect_responses(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.method in {"POST", "PUT", "PATCH"}:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response
