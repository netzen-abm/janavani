import json

class ConstitutionalPayloadExamples:
    """Provides sample JSON structures used by separate client channels to request specific export file formats."""

    @staticmethod
    def get_bill_lookup_request() -> str:
        return json.dumps({
            "bill_code": "BILL-2026-KL-04"
        })

    @staticmethod
    def get_pdf_objection_generation_request() -> str:
        return json.dumps({
            "bill_code": "BILL-2026-AS-09",
            "citizen_comments": "This rule infringes upon my right to move freely and access public services without surveillance.",
            "target_delivery_channel": "DOWNLOAD",
            "requested_file_format": "PDF"
        })

    @staticmethod
    def get_docx_objection_generation_request() -> str:
        return json.dumps({
            "bill_code": "BILL-2026-AS-09",
            "citizen_comments": "This rule infringes upon my right to move freely and access public services without surveillance.",
            "target_delivery_channel": "DOWNLOAD",
            "requested_file_format": "DOCX"
        })

