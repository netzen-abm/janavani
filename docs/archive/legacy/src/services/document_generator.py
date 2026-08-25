# Archived legacy implementation: superseded by documents.DocumentRenderer + RendererRegistry.

import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document


class MultiFormatDocumentEngine:
    """Legacy direct text-to-PDF/DOCX engine retained for historical reference."""

    @staticmethod
    def generate_pdf_stream(text_content: str) -> io.BytesIO:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        body_style = ParagraphStyle('FormalBody', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16, spaceAfter=10)
        story = [Spacer(1, 12) if line.strip() == "" else Paragraph(line, body_style) for line in text_content.split("\n")]
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer

    @staticmethod
    def generate_docx_stream(text_content: str) -> io.BytesIO:
        docx_buffer = io.BytesIO()
        doc = Document()
        for line in text_content.split("\n"):
            doc.add_paragraph(line)
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        return docx_buffer
