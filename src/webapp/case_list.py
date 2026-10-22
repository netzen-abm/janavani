"""Authenticated citizen Case-list page; summaries exclude citizen-authored content."""
from __future__ import annotations

import httpx
from fasthtml.common import A, Div, H2, Li, P, Titled, Ul
from starlette.requests import Request

from src.webapp.services.api_client import client_for_request


def register_case_list_routes(rt) -> None:
    """Register the collection view separately from single-Case lifecycle routes."""

    @rt("/cases")
    def get_case_list(request: Request):
        client = client_for_request(request)
        if not client.identity_assertion:
            return Titled(
                "Sign-in required",
                Div(
                    H2("Sign-in required"),
                    P("Sign in through Janavani to view your Cases."),
                    A("Return to dashboard", href="/"),
                ),
            )
        try:
            items = client.list_cases(limit=20)
        except (httpx.HTTPError, RuntimeError, ValueError):
            return Titled(
                "Cases temporarily unavailable",
                Div(
                    H2("Your Cases"),
                    P("Janavani could not retrieve your Case list. Your data has not been changed."),
                    A("Try again", href="/cases"),
                ),
            )
        rows = [
            Li(
                A(f"{item['case_id']} — {item['status']}", href=f"/cases/{item['case_id']}/prepare"),
                P(
                    f"Type: {item.get('case_type', 'civic case')} · "
                    f"Evidence: {item.get('evidence_count', 0)} · "
                    f"Documents: {item.get('document_count', 0)}"
                ),
            )
            for item in items
        ]
        return Titled(
            "My Janavani Cases",
            Div(
                H2("My Janavani Cases"),
                P("This list contains Case metadata only, not citizen narratives or event notes."),
                Ul(*rows) if rows else P("No Cases yet. Start one from the dashboard."),
                A("Create a Case", href="/"),
            ),
        )
