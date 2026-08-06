"""
Complaint Builder

Builds a professional complaint letter from
structured workflow data.

Pure business logic.

No Telegram.
No PDF.
No Database.
"""

from datetime import date


class ComplaintBuilder:
    """
    Builds complaint letters.
    """

    def build(
        self,
        issue: str,
        office_name: str,
        office_address: str,
        identity_mode: str = "anonymous",
        citizen: dict | None = None,
    ) -> str:

        citizen = citizen or {}

        today = date.today().strftime("%d %B %Y")

        recipient = f"""To

The Officer In Charge
{office_name}
{office_address}
"""

        subject = f"Subject: Complaint regarding {issue}"

        body = f"""
Sir/Madam,

I respectfully submit this complaint regarding the following issue:

{issue}

I kindly request your office to examine the matter and take appropriate action at the earliest.

I also request that an acknowledgement/diary/file number be communicated for future correspondence.

Thank you.
"""

        signature = self._signature(identity_mode, citizen)

        return f"""{recipient}

Date: {today}

{subject}

{body}

Yours faithfully,

{signature}
"""

    def _signature(
        self,
        identity_mode: str,
        citizen: dict,
    ) -> str:

        if identity_mode == "anonymous":
            return "Concerned Citizen"

        if identity_mode == "name":
            return citizen.get("name", "Citizen")

        return f"""{citizen.get("name", "")}

{citizen.get("address", "")}

Phone: {citizen.get("phone", "")}

Email: {citizen.get("email", "")}"""
