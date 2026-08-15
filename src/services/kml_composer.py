from typing import Dict, List, Tuple

class KmlComposerEngine:
    """
    Generates standard Keyhole Markup Language (.kml) files from coordinate lists.
    Enables instant compatibility with decentralized browsers, Freenet contracts, or Google My Maps.
    """
    @staticmethod
    def construct_kml_polygon_document(village_name: str, plots_matrix: Dict[str, List[Tuple[float, float]]]) -> str:
        """Structures text geometries into compliant KML polygons labeled cleanly by their Gata numbers."""
        kml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<kml xmlns="http://opengis.net">',
            '  <Document>',
            f'    <name>Janavani Ancestral Land Mapping Hub — {village_name}</name>',
            '    <Style id="ancestral_plot_boundary">',
            '      <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>',
            '      <PolyStyle><color>400000ff</color></PolyStyle>',
            '    </Style>'
        ]
        
        for gata_number, coordinate_pairs in plots_matrix.items():
            kml_lines.extend([
                '    <Placemark>',
                f'      <name>Gata No. {gata_number}</name>',
                '      <styleUrl>#ancestral_plot_boundary</styleUrl>',
                '      <Polygon>',
                '        <outerBoundaryIs>',
                '          <LinearRing>',
                '            <coordinates>'
            ])
            
            # Map lat/long coordinates into KML's required string format (Longitude, Latitude, Elevation)
            for lat, lon in coordinate_pairs:
                kml_lines.append(f'              {lon},{lat},0')
                
            # Close the geometric ring loop explicitly by repeating the starting coordinate pair
            if coordinate_pairs:
                first_lat, first_lon = coordinate_pairs[0]
                kml_lines.append(f'              {first_lon},{first_lat},0')
                
            kml_lines.extend([
                '            </coordinates>',
                '          </LinearRing>',
                '        </outerBoundaryIs>',
                '      </Polygon>',
                '    </Placemark>'
            ])
            
        kml_lines.extend([
            '  </Document>',
            '</kml>'
        ])
        
        return "\n".join(kml_lines)
