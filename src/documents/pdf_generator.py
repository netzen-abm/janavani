"""
PDF Generator

Converts document text into a professional PDF.

Pure rendering layer.

No Telegram.
No Database.
No Business Logic.
"""

from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate


class PDFGenerator:
    """
    Generate PDFs from plain text.
    """

    def generate(
        self,
        text: str,
        output_file: str,
    ) -> str:
        """
        Generate a PDF.

        Returns the generated filename.
        """

        document = SimpleDocTemplate(output_file)

        styles = getSampleStyleSheet()

        story = []

        for line in text.split("\n"):

            line = line.strip()

            if line == "":
                line = "&nbsp;"

            story.append(
                Paragraph(line, styles["Normal"])
            )

        document.build(story)

        return str(Path(output_file).resolve())
