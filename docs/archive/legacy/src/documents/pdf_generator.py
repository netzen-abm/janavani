# Archived 2026-08-25 before document capability convergence.
# Original active implementation preserved for audit/recovery.

from pathlib import Path
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

class PDFGenerator:
    def generate(self, text: str, output_file: str) -> str:
        document = SimpleDocTemplate(output_file)
        styles = getSampleStyleSheet()
        story = []
        for line in text.split("\n"):
            line = line.strip() or "&nbsp;"
            story.append(Paragraph(line, styles["Normal"]))
        document.build(story)
        return str(Path(output_file).resolve())
