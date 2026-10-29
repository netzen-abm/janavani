"""Deterministic civic pathway selection for JanaVani's public Dynamic Web.

This is a presentation-level map to canonical document templates. It does not
classify personal narratives, persist user stories, or perform legal analysis.
"""
from __future__ import annotations

from urllib.parse import quote

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, H3, Img, Label, Option, P, Select, Titled,
)

from src.documents.template_catalogue import get_template


PATHWAYS = {
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


def site_nav():
    """Build the shared Dynamic Web navigation."""
    return Div(
        Div(
            A(
                Img(
                    src="/brand-assets/brand/janavani-mark.svg",
                    alt="",
                    width="34",
                    height="34",
                ),
                "JANAVANI",
                href="/",
                cls="brand",
                aria_label="JanaVani home",
            ),
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


def pathway_form() -> Div:
    """Render the deterministic pathway selector."""
    return Div(
        H2("Find a civic pathway"),
        P("Choose the task you need to complete. This guided selector is deterministic; it does not classify or store your personal story."),
        Form(action="/pathway", method="post")(
            Label("What are you trying to do?"),
            Select(name="purpose", required=True)(
                Option("Choose a pathway", value="", selected=True),
                *(Option(path["label"], value=key) for key, path in PATHWAYS.items()),
            ),
            Div(
                Button("Show my pathway"),
                P("This selector sends only your pathway choice. Do not enter names, case numbers, addresses or private narratives here.", cls="hint"),
            ),
        ),
        cls="pathway-box",
    )


def register_pathway_routes(app) -> None:
    """Register the separate GET/POST pathway endpoints on the Dynamic Web app."""

    @app.get("/pathway")
    def get_pathway():
        return Titled(
            "JanaVani — Choose a Civic Pathway",
            Div(
                site_nav(),
                Div(Div(H1("Choose your civic task"), pathway_form(), cls="wrap"), cls="section"),
            ),
        )

    @app.post("/pathway")
    def post_pathway(purpose: str):
        pathway = PATHWAYS.get(purpose)
        if pathway is None:
            return Titled(
                "Choose a supported civic pathway",
                Div(
                    site_nav(),
                    Div(
                        Div(
                            H1("Choose a pathway"),
                            P("Select one of the listed tasks to continue."),
                            pathway_form(),
                            cls="wrap",
                        ),
                        cls="section",
                    ),
                ),
            )

        template = get_template(pathway["template_id"])
        draft_url = f"/ai-drafting?template_id={quote(template.template_id, safe='')}"
        return Titled(
            f"JanaVani — {pathway['label']}",
            Div(
                site_nav(),
                Div(
                    Div(
                        P("YOUR SELECTED PATHWAY", cls="eyebrow"),
                        H1(pathway["label"]),
                        P(pathway["guidance"], cls="lead"),
                        Div(
                            Div(H3("Suggested reusable format"), P(template.title), cls="card"),
                            Div(
                                H3("Before drafting"),
                                P("Confirm the competent authority, facts, available records, applicable procedure and any binding deadline."),
                                cls="card",
                            ),
                            cls="grid",
                        ),
                        Div(
                            A("Continue to this document format", href=draft_url, cls="button"),
                            A("Choose another pathway", href="/pathway", cls="button secondary"),
                            cls="actions",
                        ),
                        P(
                            "This is procedural guidance, not a legal determination. "
                            "The generated document remains editable and is never automatically submitted.",
                            cls="hint",
                        ),
                        cls="wrap",
                    ),
                    cls="section",
                ),
            ),
        )

