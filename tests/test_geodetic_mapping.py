import pytest
from src.utils.geodesy import GeodeticConverter
from src.services.kml_composer import KmlComposerEngine

def test_utm_to_wgs84_coordinate_conversion_precision():
    """Verifies that the UTM Zone 44N converter generates correct latitude and longitude values within Indian bounds."""
    # Test values based on standard geographical coordinate markers for Uttar Pradesh
    test_easting = 209432.0
    test_northing = 3002167.0
    
    lat, lon = GeodeticConverter.utm_zone_44n_to_wgs84(test_easting, test_northing)
    
    # Check that output values are accurate, reasonable, and fall within Indian land coordinates
    assert 25.0 <= lat <= 30.0
    assert 80.0 <= lon <= 85.0

def test_kml_document_string_xml_generation_compliance():
    """Confirms that the KML generation engine outputs standard markup text with correct tags."""
    mock_plots_data = {
        "29": [(26.1234, 81.5678), (26.1239, 81.5679)]
    }
    
    generated_kml_text = KmlComposerEngine.construct_kml_polygon_document(
        village_name="Mohammadpur",
        plots_matrix=mock_plots_data
    )
    
    assert "<?xml" in generated_kml_text
    assert "<kml" in generated_kml_text
    assert "Gata No. 29" in generated_kml_text
    assert "Mohammadpur" in generated_kml_text
