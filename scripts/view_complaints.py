import json

FILE_PATH = "database/complaints.jsonl"

with open(FILE_PATH, "r") as f:
    for line in f:
        data = json.loads(line)

        print("ID:", data["complaint_id"])
        print("Issue:", data["issue"])
        print("Category:", data["category"])
        print("Status:", data["status"])
        print("-" * 40)