"""Public no-login civic drafting routes; requests are never saved as Cases."""
from __future__ import annotations

from html import escape

from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from src.capabilities.anonymous_civic_drafting import (
    build_anonymous_drafts,
    recommend_document_types,
)
from src.documents.anonymous_draft_renderer import render_anonymous_draft


def _page(title: str, body: str, *, status_code: int = 200) -> HTMLResponse:
    html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{escape(title)} — Janavani</title>'
        '<style>body{font:16px/1.55 system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;color:#17212b}'
        'textarea{box-sizing:border-box;width:100%;padding:1rem;font:inherit;border:1px solid #8b98a5;border-radius:8px}'
        'button,.button{display:inline-block;padding:.65rem 1rem;margin:.35rem .25rem .35rem 0;border:0;border-radius:7px;background:#123e59;color:#fff;font:inherit;text-decoration:none;cursor:pointer}'
        '.card{border:1px solid #d5dde4;border-radius:12px;padding:1rem 1.2rem;margin:1.2rem 0}'
        '.note{background:#f2f7fa;padding:1rem;border-radius:8px}.draft{white-space:pre-wrap;overflow-wrap:anywhere;background:#f7f8fa;padding:1rem;border-radius:8px}'
        '</style></head><body><main>'
        f'<p><a href="/">← Janavani home</a></p><h1>{escape(title)}</h1>'
        f'{body}</main></body></html>'
    )
    return HTMLResponse(html, status_code=status_code, headers={
        "Cache-Control": "no-store, private",
        "Pragma": "no-cache",
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
        "X-Frame-Options": "DENY",
    })


def _selection_form(narrative: str, action: str, label: str) -> str:
    return (
        f'<form action="/draft" method="post" style="display:inline-block">'
        f'<input type="hidden" name="narrative" value="{escape(narrative, quote=True)}">'
        f'<input type="hidden" name="selection" value="{escape(action, quote=True)}">'
        f'<button type="submit">{escape(label)}</button></form>'
    )


def register_anonymous_intake_routes(rt) -> None:
    """Expose a public narrative-to-document flow, independent of login and Case persistence."""

    @rt("/draft", methods=["POST"])
    def post_anonymous_draft(
        request: Request, narrative: str = "", selection: str = "auto"
    ):
        del request
        narrative = narrative.strip()
        try:
            types, explanation = recommend_document_types(narrative)
            drafts = build_anonymous_drafts(narrative, selection)
        except ValueError as exc:
            return _page(
                "Add a little more detail",
                f'<p>{escape(str(exc))}. No Case was created.</p>'
                '<p><a href="/">Return and edit your description</a></p>',
                status_code=422,
            )

        cards = [
            '<div class="note"><strong>Suggested next step</strong><p>'
            + escape(explanation)
            + '</p><p>This is a drafting suggestion, not a legal determination. '
              'You can choose a different document below.</p></div>'
        ]
        cards.append('<section class="card"><h2>Choose a draft</h2>')
        cards.extend((
            _selection_form(narrative, "complaint", "Generate complaint only"),
            _selection_form(narrative, "rti", "Generate RTI only"),
            _selection_form(narrative, "both", "Generate both"),
        ))
        cards.append('</section>')

        for draft in drafts:
            cards.append(
                '<section class="card"><h2>' + escape(draft.title) + '</h2>'
                + '<p><strong>Subject:</strong> ' + escape(draft.subject) + '</p>'
                + '<div class="draft">' + escape(draft.body) + '</div>'
                + '<p><strong>Download this draft:</strong></p>'
                + '<form action="/draft/download" method="post" style="display:inline-block">'
                + f'<input type="hidden" name="narrative" value="{escape(narrative, quote=True)}">'
                + f'<input type="hidden" name="document_type" value="{escape(draft.document_type, quote=True)}">'
                + '<input type="hidden" name="document_format" value="pdf">'
                + '<button type="submit">Download PDF</button></form>'
                + '<form action="/draft/download" method="post" style="display:inline-block">'
                + f'<input type="hidden" name="narrative" value="{escape(narrative, quote=True)}">'
                + f'<input type="hidden" name="document_type" value="{escape(draft.document_type, quote=True)}">'
                + '<input type="hidden" name="document_format" value="docx">'
                + '<button type="submit">Download editable Word file</button></form>'
                + '</section>'
            )
        cards.append(
            '<div class="note"><strong>Your control, your choice.</strong> '
            'This no-login flow creates a document draft only. It does not create '
            'a tracked Case, contact an authority, or submit anything. Review every '
            'fact, complete the placeholders and send it yourself. Keep a local copy. '
            '<a href="/auth/login">Sign in is optional</a> for account-based tracking '
            'where that service is configured.</div>'
        )
        return _page("Review your Janavani draft", "".join(cards))

    @rt("/draft/download", methods=["POST"])
    def post_anonymous_draft_download(
        request: Request,
        narrative: str = "",
        document_type: str = "",
        document_format: str = "pdf",
    ):
        del request
        try:
            drafts = build_anonymous_drafts(narrative, document_type)
            draft = next((item for item in drafts if item.document_type == document_type), None)
            if draft is None:
                raise ValueError("Choose complaint or RTI before downloading")
            payload, media_type, extension = render_anonymous_draft(draft, document_format)
        except ValueError as exc:
            return _page(
                "Draft unavailable",
                f'<p>{escape(str(exc))}. No Case was created.</p><p><a href="/">Return home</a></p>',
                status_code=422,
            )
        return Response(
            content=payload,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="janavani-{document_type}.{extension}"',
                "Cache-Control": "no-store, private",
                "Pragma": "no-cache",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
            },
        )
