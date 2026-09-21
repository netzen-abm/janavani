"""
Issue Classifier

Classifies user issue into category + department
"""

def classify_issue(issue: str):

    issue_lower = issue.lower()

    # --------------------------------------------------
    # 🧹 SANITATION
    # --------------------------------------------------

    if any(word in issue_lower for word in [
        "garbage", "waste", "trash", "clean", "drain", "sewage"
    ]):
        return {
            "category": "Sanitation",
            "department": "Municipality / Panchayat"
        }

    # --------------------------------------------------
    # 🛣 ROAD / INFRA
    # --------------------------------------------------

    if any(word in issue_lower for word in [
        "road", "pothole", "street", "bridge"
    ]):
        return {
            "category": "Infrastructure",
            "department": "PWD (Public Works Department)"
        }

    # --------------------------------------------------
    # 💧 WATER
    # --------------------------------------------------

    if any(word in issue_lower for word in [
        "water", "pipe", "drinking water", "leak"
    ]):
        return {
            "category": "Water Supply",
            "department": "Water Authority"
        }

    # --------------------------------------------------
    # ⚡ ELECTRICITY
    # --------------------------------------------------

    if any(word in issue_lower for word in [
        "electricity", "power", "current", "transformer"
    ]):
        return {
            "category": "Electricity",
            "department": "Electricity Board"
        }

    # --------------------------------------------------
    # 🚨 DEFAULT
    # --------------------------------------------------

    return {
        "category": "General",
        "department": "Local Authority"
    }