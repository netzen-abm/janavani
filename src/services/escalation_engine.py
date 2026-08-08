"""
Escalation Engine

Determines escalation path based on category
"""

def get_escalation_targets(category: str):

    if category == "Sanitation":
        return [
            "Health Inspector",
            "Municipal Secretary",
            "District Collector"
        ]

    if category == "Infrastructure":
        return [
            "PWD Engineer",
            "Executive Engineer",
            "District Collector"
        ]

    if category == "Water Supply":
        return [
            "Water Authority Officer",
            "Assistant Engineer",
            "District Collector"
        ]

    if category == "Electricity":
        return [
            "Section Officer",
            "Assistant Engineer",
            "Electricity Board Head"
        ]

    return [
        "Local Officer",
        "District Authority",
        "State Authority"
    ]