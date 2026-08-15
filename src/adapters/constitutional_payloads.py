import json

class ConstitutionalPayloadExamples:
    """Provides sample JSON blocks used by separate client apps to run bill lookups and compile objections."""

    @staticmethod
    def get_bill_lookup_request() -> str:
        return json.dumps({
            "bill_code": "BILL-2026-KL-04"
        })

    @staticmethod
    def get_objection_generation_request() -> str:
        return json.dumps({
            "bill_code": "BILL-2026-AS-09",
            "citizen_comments": "This rule infringes upon my right to move freely and access public services without surveillance.",
            "target_delivery_channel": "PRINT_POST"
        })
