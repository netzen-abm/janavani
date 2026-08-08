from datetime import datetime
from services.escalation_engine import get_escalation_targets


# --------------------------------------------------
# 📜 LEGAL REFERENCE ENGINE
# --------------------------------------------------

def get_legal_reference(category: str):

    if category == "Sanitation":
        return "as per Municipal Solid Waste Management Rules, 2016"

    if category == "Infrastructure":
        return "as per Public Works Department (PWD) standards"

    if category == "Water Supply":
        return "as per public water supply regulations"

    if category == "Electricity":
        return "as per Electricity Supply Regulations"

    return "as per applicable public service norms"


# --------------------------------------------------
# 🧠 COMPLAINT BUILDER (INTELLIGENCE CORE)
# --------------------------------------------------

def build_complaint(
    issue: str,
    district: str = "",
    department: str = "",
    office_name: str = "",
    citizen_name: str = "Concerned Citizen",
    category: str = "General",
    complaint_id: str = None,
):

    today = datetime.now().strftime("%d %B %Y")

    # --------------------------------------------------
    # 📌 SUBJECT
    # --------------------------------------------------

    subject = f"Urgent Attention Required: {issue[:60].capitalize()}"

    if district:
        subject += f" in {district}"

    # --------------------------------------------------
    # 🏛 AUTHORITY
    # --------------------------------------------------

    authority = office_name if office_name else "The Concerned Authority"

    # --------------------------------------------------
    # ⚖ LEGAL + ESCALATION
    # --------------------------------------------------

    legal_line = get_legal_reference(category)

    escalation_targets = get_escalation_targets(category)
    escalation_text = ", ".join(escalation_targets)

    # --------------------------------------------------
    # 🆔 REFERENCE BLOCK (FIXED — SAFE)
    # --------------------------------------------------

    reference_block = ""
    if complaint_id:
        reference_block = f"Reference ID: {complaint_id}\n\n"

    # --------------------------------------------------
    # 🧾 BODY
    # --------------------------------------------------

    body = f"""
{reference_block}Date: {today}

To,
{authority}
{department}

Subject: {subject}

Sir/Madam,

I wish to bring to your attention a matter of public concern that requires immediate intervention.

Issue Description:
{issue}

This issue is causing inconvenience and poses potential risks to public safety.

Such matters are expected to be addressed {legal_line}, and it falls under your responsibility to ensure timely resolution.

I respectfully request:

1. Immediate inspection
2. Corrective action
3. Official acknowledgement

Failure to address this issue may necessitate escalation to the following authorities:
{escalation_text}

I trust appropriate action will be taken at the earliest.

Thanking you,

Yours faithfully,
{citizen_name}
"""

    return body.strip()