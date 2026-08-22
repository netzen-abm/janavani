# src/main.py
# Test the shared Janavani components.

from documents.pdf_generator import PDFGenerator
from legal_brain import get_legal_advice
from services.rate_office import save_rating
from services.search_service import search_office

print("=== JANAVANI TEST ===")
print(search_office("ration", "Kochi"))

print("\n" + "=" * 30 + "\n")

print(save_rating(office_id="3", rating=1, issue="Aadhar failed, denied ration"))

print("\n" + "=" * 30 + "\n")

legal_advice = get_legal_advice("ration denied")
document_text = "\n".join(
    [
        "Complaint — Test Citizen",
        "Address: Edathala, Kochi, Kerala",
        "Office ID: 3",
        "Issue: Aadhar failed, denied ration",
        f"Law: {legal_advice['law']}",
        f"Section: {legal_advice['section']}",
        f"Basis: {legal_advice['explanation']}",
    ]
)

pdf_file = PDFGenerator().generate(
    text=document_text,
    output_file="complaint_test.pdf",
)
print(f"Generated PDF: {pdf_file}")

print("\nDONE. Check complaint_test.pdf")
