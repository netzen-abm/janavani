import json

class ClientPayloadExamples:
    """Provides standard JSON mock blocks used by independent client apps to submit feedback and mail documents."""

    @staticmethod
    def get_feedback_submission_payload() -> str:
        return json.dumps({
            "office_id": "KL-TVM-01",
            "department_name": "Public Works Department",
            "service_rating": 5,
            "citizen_comment": "The administrative verification counter resolved my documentation request smoothly."
        })

    @staticmethod
    def get_email_dispatch_payload(tracking_id: str) -> str:
        return json.dumps({
            "tracking_id": tracking_id,
            "constituency_code": "CONSTITUENCY-AS-GHY",
            "target_tier": "MP"
        })
