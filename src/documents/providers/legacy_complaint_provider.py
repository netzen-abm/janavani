"""Adapter for the existing complaint builder.

The adapter intentionally does not call the AI/legal layer. Document generation
is deterministic from the already-approved DocumentRequest data. Legal/public
reference material must be supplied as explicit, sanitized input.
"""

from datetime import datetime, timezone
import uuid

from capabilities.document import DocumentArtifact, DocumentRequest


class LegacyComplaintProvider:
    name = "legacy-complaint-local"

    def generate(self, request: DocumentRequest) -> DocumentArtifact:
        data = dict(request.data)
        user = dict(data.get("user", {}))
        authority = dict(data.get("authority", {}))
        law = dict(data.get("law", {}))

        lines = [
            data.get("date") or datetime.now().strftime("%d-%m-%Y"),
            "",
            "To:",
            authority.get("name", ""),
            authority.get("address", ""),
            authority.get("email", ""),
            "",
        ]
        if data.get("cc"):
            lines.extend(["CC:", str(data["cc"]), ""])
        lines.extend([
            f"Subject: {data.get('subject', 'Complaint')}",
            "",
            data.get("issue", ""),
            "",
            f"Name: {user.get('name', '')}",
            f"Address: {user.get('address', '')}",
        ])
        if law:
            lines.extend([
                "",
                f"Reference: {law.get('law', '')}",
                f"Section: {law.get('section', '')}",
            ])

        content = "\n".join(lines).strip() + "\n"
        return DocumentArtifact(
            schema_version=1,
            document_id=f"DOC-{uuid.uuid4().hex[:10].upper()}",
            case_id=request.case_id,
            document_type=request.document_type,
            output_format="text" if request.output_format == "text" else request.output_format,
            content=content,
            provider=self.name,
        )
