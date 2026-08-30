"""Versioned, channel-neutral civic document template catalog."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentTemplate:
    template_id: str
    version: str
    document_type: str
    purpose: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()
    status: str = "active"


TEMPLATES = {
    "complaint": DocumentTemplate(
        template_id="JNV-COMPLAINT",
        version="1.0",
        document_type="complaint",
        purpose="Structured complaint to a responsible public authority.",
        required_fields=("authority", "subject", "issue"),
        optional_fields=("cc", "evidence", "law", "user"),
    ),
    "grievance": DocumentTemplate(
        template_id="JNV-GRIEVANCE",
        version="1.0",
        document_type="grievance",
        purpose="Structured grievance regarding a public service or decision.",
        required_fields=("authority", "subject", "issue"),
        optional_fields=("cc", "evidence", "user"),
    ),
    "rti": DocumentTemplate(
        template_id="JNV-RTI",
        version="1.0",
        document_type="rti",
        purpose="Structured request for information under the applicable RTI process.",
        required_fields=("authority", "subject", "issue"),
        optional_fields=("cc", "user"),
    ),
    "petition": DocumentTemplate(
        template_id="JNV-PETITION",
        version="1.0",
        document_type="petition",
        purpose="Structured citizen petition to a responsible authority.",
        required_fields=("authority", "subject", "issue"),
        optional_fields=("cc", "evidence", "user"),
    ),
    "representation": DocumentTemplate(
        template_id="JNV-REPRESENTATION",
        version="1.0",
        document_type="representation",
        purpose="Structured representation concerning a public matter.",
        required_fields=("authority", "subject", "issue"),
        optional_fields=("cc", "evidence", "user"),
    ),
}


def get_template(document_type: str) -> DocumentTemplate:
    try:
        return TEMPLATES[document_type.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported document type: {document_type}") from exc
