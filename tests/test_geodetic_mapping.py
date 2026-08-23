import pytest
from src.utils.geodesy import GeodeticConverter
from src.services.kml_composer import KmlComposerEngine


def test_utm_to_wgs84_coordinate_conversion_precision():
    """Verify EPSG:32644 conversion against a known Uttar Pradesh coordinate."""
    # Known WGS84 reference: approximately 26.1234 N, 81.5678 E.
    # These UTM Zone 44N values are derived from that reference and avoid
    # confusing Zone 44N with a different UTM zone.
    test_easting = 556765.1736
    test_northing = 2889473.5732

    lat, lon = GeodeticConverter.utm_zone_44n_to_wgs84(test_easting, test_northing)

    assert lat == pytest.approx(26.1234, abs=1e-4)
    assert lon == pytest.approx(81.5678, abs=1e-4)


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
