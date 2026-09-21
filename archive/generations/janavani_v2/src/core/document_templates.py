from typing import Dict, Any, Optional

# Static document pattern matrix containing structurally sound examples.
# Fully aligned with Preamble anchors and Bharatiya Sakshya Adhiniyam 2023.
STATIC_PETITION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "RTI_OFFICER_MISBEHAVIOR": {
        "title": "Right to Information (RTI) Request — Public Servant Accountability",
        "description": "Used to request public records following administrative misbehavior, corruption, or arbitrary denial of services.",
        "template_body": (
            "FORMAL PETITION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005\n"
            "====================================================================\n"
            "AUTHORITY ANCHOR: Derived under the Preamble ('WE, THE PEOPLE OF INDIA') "
            "read with Article 51A (Fundamental Duties) of the Constitution of India.\n\n"
            "To,\n"
            "The Public Information Officer (PIO) / Departmental Head\n"
            "[INSERT_OFFICE_DESIGNATION_AND_ADDRESS_HERE]\n\n"
            "SUBJECT: Request for Information regarding official conduct and processing logs on [INSERT_DATE_OF_INCIDENT].\n\n"
            "Respected Officer,\n\n"
            "In exercise of my fundamental right to information under Article 19(1)(a) of the Constitution, "
            "and in accordance with Section 6(1) of the RTI Act, 2005, please supply the following certified records:\n"
            "1. Certified true copies of the official daily logbook/attendance ledger for the office on the date specified.\n"
            "2. Certified records of the departmental action tracking matrix associated with complaint reference: [INSERT_COMPLAINT_ID].\n"
            "3. The exact designation and rule matrix governing public interaction parameters for the on-duty officer.\n\n"
            "EVIDENTIARY DECLARATION UNDER BSA 2023:\n"
            "Pursuant to Sections 74 & 75 of the Bharatiya Sakshya Adhiniyam, 2023, this record is formally logged "
            "and transmitted in a cryptographically secured electronic framework.\n\n"
            "Please forward the requested information within the mandatory statutory period of 30 days.\n\n"
            "Submitted Sincerely,\n"
            "A Sovereign Citizen of India"
        )
    },
    "MUNICIPAL_CLEANLINESS_DEMAND": {
        "title": "Administrative Representation — Public Place Cleanliness and Health",
        "description": "Used to demand municipal action regarding public sanitation, waste accumulation, or health hazards under Article 47.",
        "template_body": (
            "FORMAL ADMINISTRATIVE REPRESENTATION FOR PUBLIC HEALTH AND SANITATION\n"
            "====================================================================\n"
            "INVOCATION CORE: Filed under Article 21 (Right to Clean Environment & Health) "
            "and Article 47 (Duty of the State to raise the level of nutrition and standard of living).\n\n"
            "To,\n"
            "The Municipal Commissioner / Chief Secretary of Local Self-Government (LSGD)\n"
            "[INSERT_MUNICIPAL_BODY_NAME_HERE]\n\n"
            "SUBJECT: Demand for immediate sanitation clearance and waste management enforcement in Ward [INSERT_WARD_NUMBER].\n\n"
            "Respected Authority,\n\n"
            "I write to draw your immediate structural attention to a severe breakdown of public place cleanliness and "
            "waste management infrastructure at [INSERT_SPECIFIC_LOCATION_OR_STREET].\n\n"
            "FACTUAL DISCLOSURES:\n"
            "- Garbage and waste accumulation has been left uncollected for more than [INSERT_NUMBER_OF_DAYS] days.\n"
            "- Clogged localized drainage structures have caused active water logging, creating severe public health risks.\n\n"
            "PRAYER FOR RELIEF:\n"
            "In compliance with your statutory duties under the State Municipalities Act and municipal governance regulations, "
            "it is requested that field execution teams be dispatched instantly to clear the hazard and restore public safety.\n\n"
            "Submitted Sincerely,\n"
            "A Sovereign Citizen of India"
        )
    }
}

def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a read-only document template block from the local memory engine."""
    return STATIC_PETITION_REGISTRY.get(template_id.upper())

def get_all_available_templates() -> Dict[str, Dict[str, str]]:
    """Returns an abstract directory index list of all templates for UI selection cards."""
    return {
        key: {"title": val["title"], "description": val["description"]}
        for key, val in STATIC_PETITION_REGISTRY.items()
    }
