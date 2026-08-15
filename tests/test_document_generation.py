import pytest
import io
from src.services.document_generator import MultiFormatDocumentEngine

def test_pdf_generation_output_stream():
    """Verifies that the document engine correctly writes to an active PDF binary buffer stream."""
    sample_text = "Line 1: Constitutional Violation Analysis\nLine 2: Section 4 Details"
    
    pdf_stream = MultiFormatDocumentEngine.generate_pdf_stream(sample_text)
    
    assert pdf_stream is not None
    assert isinstance(pdf_stream, io.BytesIO)
    
    binary_data = pdf_stream.getvalue()
    # Confirm the output matches the standard binary header definition for PDFs
    assert binary_data.startswith(b"%PDF")

def test_docx_generation_output_stream():
    """Verifies that the document engine correctly writes to an active Word .docx binary buffer stream."""
    sample_text = "Line 1: Constitutional Violation Analysis\nLine 2: Section 4 Details"
    
    docx_stream = MultiFormatDocumentEngine.generate_docx_stream(sample_text)
    
    assert docx_stream is not None
    assert isinstance(docx_stream, io.BytesIO)
    
    binary_data = docx_stream.getvalue()
    # Confirm the output matches the standard zip archive binary header format used by Microsoft Office files
    assert binary_data.startswith(b"PK")
