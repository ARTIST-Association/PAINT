import math
from typing import List, Tuple

import paint.util.paint_mappings as mappings


def add_offset_to_lat_lon(
    north_offset_m: float, east_offset_m: float
) -> Tuple[float, float]:
    """
    Add an offset to the given latitude and longitude coordinates.

    Parameters
    ----------
    north_offset_m : float
        The distance in meters to add to the latitude.
    east_offset_m : float
        The distance in meters to add to the longitude.

    Returns
    -------
    float
        The new latitude in degrees.
    float
        The new longitude in degrees.
    """
    # Convert latitude and longitude to radians
    lat_rad = math.radians(mappings.POWER_PLANT_LAT)
    lon_rad = math.radians(mappings.POWER_PLANT_LON)

    # Calculate meridional radius of curvature
    sin_lat = math.sin(lat_rad)
    rn = mappings.WGS84_A / math.sqrt(1 - mappings.WGS84_E2 * sin_lat**2)

    # Calculate transverse radius of curvature
    rm = (mappings.WGS84_A * (1 - mappings.WGS84_E2)) / (
        (1 - mappings.WGS84_E2 * sin_lat**2) ** 1.5
    )

    # Calculate new latitude
    dlat = north_offset_m / rm
    new_lat_rad = lat_rad + dlat

    # Calculate new longitude using the original meridional radius of curvature
    dlon = east_offset_m / (rn * math.cos(lat_rad))
    new_lon_rad = lon_rad + dlon

    # Convert back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon


def calculate_heliostat_position_in_m_from_lat_lon(
    lat1: float, lon1: float, alt: float
) -> List[float]:
    """
    Calculate the position of a heliostat in meters from given latitude, longitude, and altitude.

    This function calculates the north and east offsets in meters of a heliostat from the power plant location.
    It converts the latitude and longitude to radians, calculates the radius of curvature values,
    and then computes the offsets based on the differences between the heliostat and power plant coordinates.
    Finally, it returns a list containing these offsets along with the altitude difference.

    Parameters
    ----------
    lat1 : float
        The latitude of the heliostat in degrees.
    lon1 : float
        The longitude of the heliostat in degrees.
    alt : float
        The altitude of the heliostat.

    Returns
    -------
    List[float, float, float]
        The north offset in meters, east offset in meters, and the altitude difference from the power plant.
    """
    # Convert latitude and longitude to radians
    lat_heliostat_rad = math.radians(lat1)
    lon_heliostat_rad = math.radians(lon1)
    alt_heliostat = alt - mappings.POWER_PLANT_ALT
    lat_tower_rad = math.radians(mappings.POWER_PLANT_LAT)
    lon_tower_rad = math.radians(mappings.POWER_PLANT_LON)

    # Calculate meridional radius of curvature for the first latitude
    sin_lat1 = math.sin(lat_heliostat_rad)
    rn1 = mappings.WGS84_A / math.sqrt(1 - mappings.WGS84_E2 * sin_lat1**2)

    # Calculate transverse radius of curvature for the first latitude
    rm1 = (mappings.WGS84_A * (1 - mappings.WGS84_E2)) / (
        (1 - mappings.WGS84_E2 * sin_lat1**2) ** 1.5
    )

    # Calculate delta latitude and delta longitude in radians
    dlat_rad = lat_tower_rad - lat_heliostat_rad
    dlon_rad = lon_tower_rad - lon_heliostat_rad

    # Calculate north and east offsets in meters
    north_offset_m = dlat_rad * rm1
    east_offset_m = dlon_rad * rn1 * math.cos(lat_heliostat_rad)
    return [north_offset_m, east_offset_m, alt_heliostat]
