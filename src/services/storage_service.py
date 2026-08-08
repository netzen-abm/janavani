import json
from datetime import datetime

FILE_PATH = "database/complaints.jsonl"


# --------------------------------------------------
# 💾 SAVE COMPLAINT
# --------------------------------------------------

def save_complaint(session: dict):

    record = {
        "complaint_id": session.get("complaint_id"),
        "issue": session.get("issue"),
        "category": session.get("category"),
        "department": session.get("department"),
        "district": session.get("district"),
        "office": session.get("office"),
        "created_at": datetime.now().isoformat(),
        "status": "Pending"
    }

    with open(FILE_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


# --------------------------------------------------
# 🔍 FETCH COMPLAINT BY ID
# --------------------------------------------------

def get_complaint_by_id(complaint_id: str):

    try:
        with open(FILE_PATH, "r") as f:
            for line in f:
                record = json.loads(line)

                if record.get("complaint_id") == complaint_id:
                    return record

    except FileNotFoundError:
        return None

    return None