# src/main.py
# Test the whole system (fixed imports and path handling)

import os
import sys

# Ensure the src/ directory is on sys.path so package-style imports work when running this file directly
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from services.search_directory import search_office
from services.rate_office import save_rating
from documents.generate_pdf import generate_complaint_pdf
from legal_brain import get_legal_advice


def main():
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


if __name__ == "__main__":
    main()
