"""WebApp adapter for the reusable civic-drafting presentation routes.

Identity remains request-scoped to this WebApp. The shared form/preview UI is
in src.ui.civic_drafting and the canonical API owns drafting workflow policy.
"""
from src.ui.civic_drafting_routes import register_civic_drafting_routes
from src.webapp.services.api_client import client_for_request


def register_ai_drafting_routes(rt) -> None:
    """Register the shared drafting journey using the WebApp's request identity."""
    register_civic_drafting_routes(
        rt,
        client_factory=lambda request: client_for_request(request),
    )
