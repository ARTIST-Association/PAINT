from pyproj import Transformer


def convert_gk_to_lat_long(right: float, height: float) -> tuple[float, float]:
    """
    Convert a Gauss-Kruger coordinate to a latitude / longitude coordinate.

    Parameters
    ----------
    right : float
        The right coordinate from the Gauss-Krueger coordinate system.
    height : float
        The height of the Gauss-Krueger coordinate system.

    Returns
    -------
    float
        The converted latitude.
    float
        The converted longitude.
    """
    # Define the source (Gauss-Kruger zone 2) and target (WGS84) coordinate systems using CRS.
    gk_zone2_configuration = (
        "epsg:31466"  # Equivalent to Gauss-Kruger zone 2 in EPSG code
    )
    wgs84_configuration = "epsg:4326"  # WGS84 coordinate system

    # Create a Transformer object to convert between the two coordinate systems.
    transformer = Transformer.from_crs(
        gk_zone2_configuration, wgs84_configuration, always_xy=True
    )

    # Perform the conversion
    lon, lat = transformer.transform(right, height)

    # Return latitude and longitude in correct order, pyproj returns the reverse order.
    return lat, lon
