# src/legal_brain.py
# Janavani Legal Engine v1.0
# Cites Constitution, BSA, IT Act, Consumer Act, Contract Act

LEGAL_DATABASE = {
    "ration_denied": {
        "law": "Consumer Protection Act, 2019",
        "section": "Section 2(11) - Deficiency in Service",
        "explanation": "Denial of entitled ration due to Aadhar failure is deficiency in service by Civil Supplies Department."
    },
    "hospital_misbehavior": {
        "law": "Constitution of India",
        "section": "Article 21 - Right to Life",
        "explanation": "Right to health is part of Right to Life. Denial of treatment violates fundamental rights."
    },
    "hospital_no_bed": {
        "law": "The Clinical Establishments Act, 2010",
        "section": "Section 12 - Display of Rates and Facilities",
        "explanation": "Citizens have right to know availability of beds and emergency services."
    },
    "police_misbehavior": {
        "law": "Bhartiya Nyaya Sanhita, 2023",
        "section": "Section 217 - Public servant disobeying direction of law",
        "explanation": "Police officer refusing to register complaint or misbehaving is an offense."
    },
    "panchayat_delay": {
        "law": "Kerala Panchayat Raj Act, 1994",
        "section": "Section 272 - Duty to provide services",
        "explanation": "Unreasonable delay in issuing certificate is dereliction of duty."
    },
    "mvd_corruption": {
        "law": "The Prevention of Corruption Act, 1988",
        "section": "Section 7 - Public servant taking bribe",
        "explanation": "Demanding money for license/RC is punishable."
    },
    "data_leak": {
        "law": "Information Technology Act, 2000",
        "section": "Section 43A - Compensation for failure to protect data",
        "explanation": "Govt body leaking Aadhar/other data is liable."
    },
    "contract_cheating": {
        "law": "Indian Contract Act, 1872",
        "section": "Section 17 - Fraud",
        "explanation": "Misrepresentation in govt contract/tender is fraud."
    }
}

def get_legal_advice(issue_keyword: str) -> dict:
    """
    Input: "ration_denied"
    Output: Law, Section, Explanation to put in PDF
    """
    issue_keyword = issue_keyword.lower().replace(" ", "_")

    for key in LEGAL_DATABASE:
        if key in issue_keyword:
            return LEGAL_DATABASE[key]

    # Default fallback
    return {
        "law": "Constitution of India",
        "section": "Article 14 - Right to Equality",
        "explanation": "Citizens have right to equal and fair treatment by government."
    }

# Example usage
if __name__ == "__main__":
    print(get_legal_advice("ration denied"))
