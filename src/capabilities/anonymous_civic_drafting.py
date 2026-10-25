"""Pure, non-persistent complaint/RTI drafting for anonymous first-use journeys.

This capability classifies the user's stated goal and prepares editable drafts.
It does not create Cases, resolve liability, select an unverified authority,
persist narratives, or submit anything.
"""
from __future__ import annotations

import re

from src.documents.anonymous_draft_contract import AnonymousCivicDraft


_MAX_NARRATIVE_CHARS = 5_000
_DOCUMENT_TYPES = ("complaint", "rti")


def recommend_document_types(narrative: str) -> tuple[tuple[str, ...], str]:
    """Suggest an action type from text without asserting legal facts."""
    text = " ".join(narrative.casefold().split())
    if not text:
        raise ValueError("Describe the incident before generating a draft")

    information_markers = (
        "rti", "right to information", "information", "records", "record copy",
        "copy of", "copies of", "file noting", "action taken report", "atr",
        "funds spent", "expenditure", "tender", "work order", "sanction order",
        "status of my application", "who approved", "inspection report",
        "documents", "details of", "provide data", "how much was spent",
    )
    remedy_markers = (
        "broken", "damaged", "not working", "not received", "not delivered",
        "delay", "delayed", "leak", "garbage", "waste", "pothole", "streetlight",
        "sewage", "unsafe", "repair", "fix", "remove", "blocked", "denied",
        "pending", "no action", "no response", "harassment", "bribe",
        "corruption", "problem", "complaint", "grievance", "please help",
    )
    seeks_information = any(marker in text for marker in information_markers)
    seeks_remedy = any(marker in text for marker in remedy_markers)
    if seeks_information and seeks_remedy:
        return ("complaint", "rti"), (
            "Your description includes both a problem needing attention and a request "
            "for official information, so Janavani recommends preparing both drafts."
        )
    if seeks_information:
        return ("rti",), (
            "Your description focuses on records, facts, or status that a public "
            "authority may hold, so an RTI draft is the recommended starting point."
        )
    return ("complaint",), (
        "Your description primarily describes a problem needing attention, so a "
        "complaint draft is the recommended starting point. Choose RTI instead if "
        "your main aim is to obtain existing official records."
    )


def build_anonymous_drafts(
    narrative: str, selection: str = "auto"
) -> tuple[AnonymousCivicDraft, ...]:
    """Prepare one or both draft documents without creating a Case or storing text."""
    incident = narrative.strip()
    if not incident or len(incident) > _MAX_NARRATIVE_CHARS:
        raise ValueError("Describe the incident in 1 to 5,000 characters")
    if len(incident.split()) < 2:
        raise ValueError("Please describe the incident in a complete sentence")
    recommended, _reason = recommend_document_types(incident)
    selected = selection.strip().casefold()
    types = recommended if selected == "auto" else (
        ("complaint", "rti") if selected == "both" else (selected,)
    )
    if not types or any(item not in _DOCUMENT_TYPES for item in types):
        raise ValueError("Choose auto, complaint, rti, or both")

    subject = _subject_from_incident(incident)
    return tuple(_build_one(item, incident, subject) for item in types)


def _subject_from_incident(incident: str) -> str:
    first_line = next((line.strip() for line in incident.splitlines() if line.strip()), incident)
    clean = re.sub(r"\s+", " ", first_line).strip(" .;:")
    return clean[:120] or "Request concerning a civic matter"


def _build_one(kind: str, incident: str, subject: str) -> AnonymousCivicDraft:
    if kind == "rti":
        title = "Draft application seeking information under the RTI Act"
        body = f"""To
The Central/State Public Information Officer (as applicable)
[Name of the concerned public authority and postal address]

Date: [Enter date]
Applicant: [Fill your name and postal address before sending]

Subject: Request for existing records concerning {subject}

Sir/Madam,

I request access to the following existing records held by your public authority under the Right to Information Act, 2005, subject to the Act and applicable rules.

Matter described by the applicant:
{incident}

Information and records requested:
1. Copies of the relevant register entries, complaint/representation records, file notings and correspondence held by your office concerning the matter described above.
2. Copies of orders, inspection reports, work orders, decisions or action-taken records concerning this matter, where such records exist and are held by your office.
3. The status and dates of action recorded in the relevant file or register, and the name/designation of the office handling the matter as shown in official records.
4. The relevant record period is: [Specify dates or period as precisely as possible].

Please provide the records electronically where available. If the requested information, or part of it, is held by another public authority, please consider transfer under section 6(3) where applicable and inform me.

I understand that disclosure is subject to the RTI Act, applicable exemptions and prescribed fees. This application seeks existing information and records; it is not a request for a grievance decision or for an explanation to be newly created.

Yours faithfully,
[Applicant name]
[Postal address and contact details needed for delivery]
[Attach/complete prescribed fee details, where applicable]

DRAFT ONLY — Janavani has not submitted this application. Confirm the correct Public Information Officer, narrow the records and date range, complete required fields, and review the applicable State/Central rules before sending."""
    else:
        title = "Draft civic complaint / grievance representation"
        body = f"""To
The Appropriate Officer / Head of the Concerned Public Authority
[Department, office and postal address]

Date: [Enter date]
Complainant: [Fill your name and contact details if you choose]

Subject: Request to examine and address — {subject}

Sir/Madam,

I wish to bring the following civic/public-service issue to the attention of the competent office:

Incident as described by me:
{incident}

I respectfully request that your office:
1. Register and acknowledge this representation, and provide a reference number if available.
2. Verify the reported facts and inspect or review the matter where appropriate.
3. Take corrective action in accordance with applicable rules if the issue is confirmed.
4. Inform me of the action taken, current status, or the office responsible for the next step.

Location/ward/asset: [Add if known]
Date or period of incident: [Add if known]
Earlier complaint/reference and supporting material: [Add if available]

I have stated the incident as I understand it. Please examine the matter and respond through the appropriate process.

Yours faithfully,
[Name — complete locally]
[Postal address/contact details — include only what the authority requires]

DRAFT ONLY — Janavani has not registered a Case or submitted this complaint. Verify the facts, office, dates and any applicable procedure before sending."""
    return AnonymousCivicDraft(kind, title, subject, body)
