# src/documents/complaint_builder.py

import datetime
from legal_brain import get_legal_advice


def build_complaint(user_name: str, user_address: str, office_id: str, issue_text: str) -> dict:
    """
    Builds structured complaint data
    This does NOT generate PDF
    """

    # 1. Generate complaint ID (centralized here)
    complaint_id = f"JV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 2. Get legal grounding
    law_data = get_legal_advice(issue_text)

    # 3. Date
    today = datetime.date.today().strftime("%d-%m-%Y")

    # 4. Structured output
    return {
        "complaint_id": complaint_id,
        "date": today,
        "user": {
            "name": user_name,
            "address": user_address
        },
        "office_id": office_id,
        "issue": issue_text,
        "law": law_data
    }