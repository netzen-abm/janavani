"""
Issue Classification Engine

This version is rule based.

Later this file will call AI
only if no rule matches.
"""


ISSUE_RULES = [

    {
        "keywords": [
            "road",
            "pothole",
            "broken road",
            "street"
        ],
        "department": "PWD",
        "document": "Complaint"
    },

    {
        "keywords": [
            "water",
            "pipe",
            "leak",
            "drinking water"
        ],
        "department": "Kerala Water Authority",
        "document": "Complaint"
    },

    {
        "keywords": [
            "garbage",
            "waste",
            "dump",
            "cleaning"
        ],
        "department": "Municipality",
        "document": "Complaint"
    },

    {
        "keywords": [
            "ration",
            "ration card",
            "food"
        ],
        "department": "Civil Supplies",
        "document": "Complaint"
    },

    {
        "keywords": [
            "aadhar",
            "aadhaar",
            "uidai"
        ],
        "department": "UIDAI",
        "document": "Complaint"
    },

    {
        "keywords": [
            "information",
            "records",
            "details",
            "copy",
            "documents"
        ],
        "department": "Unknown",
        "document": "RTI"
    }

]


def classify_issue(issue):

    issue = issue.lower()

    for rule in ISSUE_RULES:

        for keyword in rule["keywords"]:

            if keyword in issue:

                return {

                    "department": rule["department"],

                    "document": rule["document"],

                    "matched_keyword": keyword
                }

    return {

        "department": "Unknown",

        "document": "Complaint",

        "matched_keyword": None
    }
