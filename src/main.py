# src/main.py
# Test the whole system

from src.tools.search_directory import search_office
from src.tools.rate_office import save_rating
from src.tools.generate_pdf import generate_complaint_pdf
from src.legal_brain import get_legal_advice

print("=== JANAVANI TEST ===")
print(search_office("ration", "Kochi"))

print("\n" + "="*30 + "\n")

print(save_rating(office_id="3", rating=1, issue="Aadhar failed, denied ration"))

print("\n" + "="*30 + "\n")

print(generate_complaint_pdf(
    user_name="Test Citizen",
    user_address="Edathala, Kochi, Kerala",
    office_id="3", 
    issue_text="Aadhar failed, denied ration"
))

print("\nDONE. Check for complaint_xxx.pdf file")
