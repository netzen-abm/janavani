"""Archived 2026-08-25 before document capability convergence.

Original active implementation is preserved verbatim for recovery/audit.
See the convergence branch for the canonical replacement.
"""

"""
Document Engine

Central entry point for all document generation.

Supported document types:

- Complaint
- RTI
- Petition
- Grievance

Additional document types can be registered
without changing conversation logic.
"""

from documents.complaint_builder import ComplaintBuilder


class DocumentEngine:
    """
    Builds structured legal documents.

    This class acts as the public interface
    between the Workflow Engine and the
    individual document builders.
    """

    def __init__(self):
        self.complaint_builder = ComplaintBuilder()

    def generate(
        self,
        document_type: str,
        **kwargs,
    ):
        """
        Generate a document.
        """
        document_type = document_type.lower()
        if document_type == "complaint":
            return self.complaint_builder.build(**kwargs)
        raise ValueError(f"Unsupported document type: {document_type}")
