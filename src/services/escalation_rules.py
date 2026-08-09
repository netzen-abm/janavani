# src/services/escalation_rules.py

def get_escalation_targets(category: str):
    """
    Returns escalation hierarchy based on complaint category
    """

    if category == "Sanitation":
        return [
            "Health Inspector",
            "Municipal Secretary",
            "District Collector"
        ]

    elif category == "Infrastructure":
        return [
            "PWD Engineer",
            "Executive Engineer",
            "District Collector"
        ]

    elif category == "Water Supply":
        return [
            "Water Authority Officer",
            "Assistant Engineer",
            "District Collector"
        ]

    elif category == "Electricity":
        return [
            "Section Officer",
            "Assistant Engineer",
            "Electricity Board Head"
        ]

    else:
        return [
            "Local Officer",
            "District Authority",
            "State Authority"
        ]