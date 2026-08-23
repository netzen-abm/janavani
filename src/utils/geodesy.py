import math
from typing import Tuple


class GeodeticConverter:
    """
    Convert UTM Zone 44N (EPSG:32644) coordinates to WGS84 latitude/longitude.

    The inverse projection is implemented locally so the conversion can run in
    server or WebAssembly environments without an external geospatial service.
    """

    @staticmethod
    def utm_zone_44n_to_wgs84(easting: float, northing: float) -> Tuple[float, float]:
        """Convert UTM Zone 44N easting/northing to WGS84 latitude/longitude."""
        # WGS84 / UTM constants.
        semi_major_axis = 6378137.0
        eccentricity_squared = 0.00669438
        scale_factor = 0.9996
        central_meridian = 81.0

        x = easting - 500000.0
        y = northing
        eccentricity_prime_squared = eccentricity_squared / (1.0 - eccentricity_squared)

        meridional_arc = y / scale_factor
        mu = meridional_arc / (
            semi_major_axis
            * (
                1.0
                - eccentricity_squared / 4.0
                - 3.0 * eccentricity_squared**2 / 64.0
                - 5.0 * eccentricity_squared**3 / 256.0
            )
        )

        e1 = (1.0 - math.sqrt(1.0 - eccentricity_squared)) / (
            1.0 + math.sqrt(1.0 - eccentricity_squared)
        )
        footpoint_latitude = (
            mu
            + (3.0 * e1 / 2.0 - 27.0 * e1**3 / 32.0) * math.sin(2.0 * mu)
            + (21.0 * e1**2 / 16.0 - 55.0 * e1**4 / 32.0) * math.sin(4.0 * mu)
            + (151.0 * e1**3 / 96.0) * math.sin(6.0 * mu)
            + (1097.0 * e1**4 / 512.0) * math.sin(8.0 * mu)
        )

        sin_fp = math.sin(footpoint_latitude)
        cos_fp = math.cos(footpoint_latitude)
        tan_fp = math.tan(footpoint_latitude)

        n1 = semi_major_axis / math.sqrt(1.0 - eccentricity_squared * sin_fp**2)
        r1 = (
            semi_major_axis
            * (1.0 - eccentricity_squared)
            / (1.0 - eccentricity_squared * sin_fp**2) ** 1.5
        )
        t1 = tan_fp**2
        c1 = eccentricity_prime_squared * cos_fp**2
        d = x / (n1 * scale_factor)

        latitude = footpoint_latitude - (
            n1
            * tan_fp
            / r1
            * (
                d**2 / 2.0
                - (5.0 + 3.0 * t1 + 10.0 * c1 - 4.0 * c1**2 - 9.0 * eccentricity_prime_squared)
                * d**4
                / 24.0
                + (
                    61.0
                    + 90.0 * t1
                    + 298.0 * c1
                    + 45.0 * t1**2
                    - 252.0 * eccentricity_prime_squared
                    - 3.0 * c1**2
                )
                * d**6
                / 720.0
            )
        )

        longitude = (
            d
            - (1.0 + 2.0 * t1 + c1) * d**3 / 6.0
            + (
                5.0
                - 2.0 * c1
                + 28.0 * t1
                - 3.0 * c1**2
                + 8.0 * eccentricity_prime_squared
                + 24.0 * t1**2
            )
            * d**5
            / 120.0
        ) / cos_fp

        return math.degrees(latitude), central_meridian + math.degrees(longitude)
