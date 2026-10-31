"""Public content pages for the Dynamic Web presentation boundary.

These page renderers reuse the canonical pathway and drafting routes; they do
not own legal rules, identity, persistence, or drafting orchestration.
"""
from __future__ import annotations

from fasthtml.common import A, Div, H1, H2, H3, Img, P, Title

from src.dynamic_web.pathways import pathway_form, site_nav


def register_public_pages(rt) -> None:
    """Register public landing and processing-disclosure pages."""

    @rt("/")
    def get_home():
        """Render the public landing page without requiring the API or Telegram."""
        return (
            Title("JanaVani — The Infrastructure of Citizen Voice"),
            Div(
                site_nav(),
                Div(
                    Div(
                        P("THE INFRASTRUCTURE OF CITIZEN VOICE", cls="eyebrow"),
                        H1("WE, THE PEOPLE OF INDIA"),
                        P(
                            "Civic infrastructure for meaningful citizen participation. "
                            "Understand a public issue, choose an appropriate civic pathway, "
                            "and prepare a document you can review and edit.",
                            cls="lead",
                        ),
                        Div(
                            A("Find a civic pathway", href="/pathway", cls="button"),
                            A(
                                "Draft a civic document",
                                href="/ai-drafting",
                                cls="button secondary",
                            ),
                            cls="actions",
                        ),
                        cls="wrap",
                    ),
                    cls="hero",
                ),
                Div(
                    Div(
                        Img(
                            src="/brand-assets/illustrations/preamble-of-india",
                            alt="Visual rendering of the Preamble of the Constitution of India",
                            loading="lazy",
                            decoding="async",
                            cls="preamble-visual",
                        ),
                        H2("From citizen concern to informed action"),
                        P(
                            "JanaVani helps make civic procedures easier to navigate. It is "
                            "not a government authority, court, or substitute for qualified "
                            "legal advice."
                        ),
                        Div(
                            Div(
                                H3("Complaint"),
                                P(
                                    "Describe a problem and ask the responsible authority "
                                    "to examine it."
                                ),
                                cls="card",
                            ),
                            Div(
                                H3("RTI"),
                                P(
                                    "Request existing records with a clear public authority "
                                    "and record list."
                                ),
                                cls="card",
                            ),
                            Div(
                                H3("Representation"),
                                P(
                                    "Present a position and request lawful administrative "
                                    "consideration."
                                ),
                                cls="card",
                            ),
                            cls="grid",
                        ),
                        Img(
                            src="/brand-assets/illustrations/civic-action-pathway",
                            alt="JanaVani civic action pathway visual",
                            loading="lazy",
                            decoding="async",
                            cls="pathway-visual",
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
                            "Draft previews are sent to the configured JanaVani preview API "
                            "for transient processing and are not saved or submitted by this "
                            "site. Remote AI is currently disabled for raw free-text narratives "
                            "until privacy-safe input minimization is proven."
                        ),
                        P(
                            "Review all facts, recipients, statutory references and deadlines "
                            "before use. A polished draft is not proof that its claims are true."
                        ),
                        A("Read the processing boundary", href="/privacy"),
                        cls="wrap intro",
                    ),
                    cls="section",
                ),
                Div(
                    Div(P("JanaVani · Public Dynamic Web · Independent runtime"), cls="wrap"),
                    cls="footer",
                ),
            ),
        )

    @rt("/privacy")
    def get_privacy():
        """Explain processing boundaries in citizen-facing language."""
        return (
            Title("JanaVani — Processing and Privacy"),
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
                            "When you request a draft preview, the issue, selected fields and "
                            "any pasted draft are sent to the configured JanaVani preview API "
                            "for transient processing. The preview is not saved or submitted "
                            "by this site."
                        ),
                        H2("Remote AI status"),
                        P(
                            "Remote AI is temporarily disabled for unrestricted free-text "
                            "issue narratives and pasted drafts. Deterministic drafting remains "
                            "available. Do not include unnecessary personal or sensitive details."
                        ),
                        H2("Your control"),
                        P(
                            "Review the draft before use. Verify facts, recipients, disclosure "
                            "processes, statutes and deadlines. JanaVani does not automatically "
                            "submit or email documents."
                        ),
                        A("Return home", href="/"),
                        cls="wrap intro",
                    ),
                    cls="section",
                ),
            ),
        )
