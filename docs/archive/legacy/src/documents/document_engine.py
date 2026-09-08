# Archived legacy implementation preserved before retirement.
# Source: src/documents/document_engine.py
#
# This module depended on the legacy ComplaintBuilder and is not an
# authoritative document-generation path. Canonical document generation now
# flows through CivicActionCapability -> DocumentDraft -> artifact service.

"""
Document Engine

Central entry point for all document generation.

Supported document types:
- Complaint
- RTI
- Petition
- Grievance
"""

from documents.complaint_builder import ComplaintBuilder


class DocumentEngine:
    """Legacy structured-document dispatcher retained for audit history."""

    def __init__(self):
        self.complaint_builder = ComplaintBuilder()

    def generate(self, document_type: str, **kwargs):
        document_type = document_type.lower()
        if document_type == "complaint":
            return self.complaint_builder.build(**kwargs)
        raise ValueError(f"Unsupported document type: {document_type}")
