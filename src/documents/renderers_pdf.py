"""PDF adapter for the canonical DocumentDraft contract."""
from __future__ import annotations

from html import escape
from pathlib import Path

from weasyprint import HTML

from src.documents.document_contract import DocumentDraft


class PdfDocumentRenderer:
    """Render a DocumentDraft to PDF; never send or submit it."""

    def render(self, draft: DocumentDraft, output_dir: str | Path) -> Path:
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{draft.document_id}.pdf"
        html = self._html(draft)
        HTML(string=html).write_pdf(str(path))
        return path

    @staticmethod
    def _html(draft: DocumentDraft) -> str:
        cc = "".join(
            f"<p>{escape(p.role or p.name)}<br>{escape(p.name)}<br>"
            f"{escape(p.address)}"
            + (f"<br>Email: {escape(p.email)}" if p.email else "")
            + "</p>"
            for p in draft.cc
        )
        sender = ""
        if draft.sender:
            sender = (
                "<section><strong>From:</strong><br>"
                f"{escape(draft.sender.name)}<br>{escape(draft.sender.address)}"
                + (
                    f"<br>Email: {escape(draft.sender.email)}"
                    if draft.sender.email
                    else ""
                )
                + "</section>"
            )
        legal = ""
        if draft.legal_ground:
            legal = (
                "<section><strong>Legal Ground:</strong>"
                f"<br>{escape(draft.legal_ground)}</section>"
            )
        return f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; margin: 42px; line-height: 1.45; }}
h1 {{ text-align: center; font-size: 20px; }}
section {{ margin: 22px 0; }}
.subject {{ font-weight: bold; margin-top: 20px; }}
</style></head><body>
<h1>{escape(draft.document_type.upper())}</h1>
<p><strong>Document ID:</strong> {escape(draft.document_id)}<br>
<strong>Case ID:</strong> {escape(draft.case_id)}<br>
<strong>Date:</strong> {escape(draft.date)}</p>
<section><strong>To:</strong><br>
{escape(draft.to.role or draft.to.name)}<br>
{escape(draft.to.name)}<br>{escape(draft.to.address)}
{f"<br>Email: {escape(draft.to.email)}" if draft.to.email else ""}</section>
{sender}
<div class="subject">Subject: {escape(draft.subject)}</div>
<section>{escape(draft.body).replace(chr(10), '<br>')}</section>
{legal}
<section><strong>CC:</strong>{cc}</section>
</body></html>
"""
