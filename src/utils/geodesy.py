import math
from typing import Tuple, List

class GeodeticConverter:
    """
    Converts Universal Transverse Mercator (UTM) Zone 44N projection grids (EPSG:32644)
    commonly found on state BhuNaksha map systems into standard WGS84 Lat/Long coordinates.
    Runs entirely locally within WebAssembly (WASM) or server runtimes without external calls.
    """
    @staticmethod
    def utm_zone_44n_to_wgs84(easting: float, northing: float) -> Tuple[float, float]:
        """Mathematical conversion formulation from UTM Zone 44N projection map bounds back to Lat/Long formats."""
        # Baseline projection grid constants for UTM Zone 44N (Central Meridian = 81 degrees East)
        sa = 6378137.0
        sb = 6356752.3142
        
        e2 = (((sa ** 2) - (sb ** 2)) ** 0.5) / sa
        e2_sq = e2 ** 2
        c_meridian = 81.0
        
        x = easting - 500000.0
        y = northing
        
        # Approximate geometric meridian map projection routing metrics
        m = y / 0.9996
        mu = m / (sa * (1.0 - e2_sq / 4.0 - 3.0 * e2_sq * e2_sq / 64.0 - 5.0 * (e2_sq ** 3) / 256.0))
        
        phi1 = mu + (3.0 * e2_sq / 2.0 - 27.0 * (e2_sq ** 3) / 32.0) * math.sin(2.0 * mu)
        c1 = (e2_sq / (1.0 - e2_sq)) * (math.cos(phi1) ** 2)
        t1 = math.tan(phi1) ** 2
        n1 = sa / ((1.0 - e2_sq * (math.sin(phi1) ** 2)) ** 0.5)
        r1 = sa * (1.0 - e2_sq) / ((1.0 - e2_sq * (math.sin(phi1) ** 2)) ** 1.5)
        d = x / (n1 * 0.9996)
        
        lat = phi1 - (n1 * math.tan(phi1) / r1) * ((d ** 2) / 2.0 - (5.0 + 3.0 * t1 + 10.0 * c1 - 4.0 * (c1 ** 2) - 9.0 * e2_sq) * (d ** 4) / 24.0)
        lon = (d - (1.0 + 2.0 * t1 + c1) * (d ** 3) / 6.0 + (5.0 + 28.0 * t1 + 24.0 * (t1 ** 2) + 6.0 * c1 + 8.0 * (c1 ** 2)) * (d ** 5) / 120.0) / math.cos(phi1)
        
        latitude = math.degrees(lat)
        longitude = c_meridian + math.degrees(lon)
        
        return latitude, longitude
