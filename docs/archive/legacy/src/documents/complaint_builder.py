# Archived legacy implementation preserved before retirement.
# Source: src/documents/complaint_builder.py
#
# This implementation constructs complaint data from free-form user/office
# inputs and invokes legacy legal_brain logic. It is not authoritative and
# must not be used for canonical civic document generation.

import datetime
from legal_brain import get_legal_advice


def build_complaint(user_name: str, user_address: str, office_id: str, issue_text: str) -> dict:
    complaint_id = f"JV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    law_data = get_legal_advice(issue_text)
    today = datetime.date.today().strftime("%d-%m-%Y")
    return {
        "complaint_id": complaint_id,
        "date": today,
        "user": {"name": user_name, "address": user_address},
        "office_id": office_id,
        "issue": issue_text,
        "law": law_data,
    }
