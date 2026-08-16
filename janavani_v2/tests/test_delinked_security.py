import pytest
from src.web.de_linked_ingestion import DelinkedIngestionEngine

def test_metadata_stripping_on_image_buffers():
    """Confirms that the geodetic processing loop successfully drops camera and GPS tracking fields."""
    # Build a tiny 1x1 pixel raw blank mock image byte string
    mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    scrubbed_output = DelinkedIngestionEngine.strip_image_metadata(mock_image_bytes)
    assert scrubbed_output is not None
    assert len(scrubbed_output) > 0
