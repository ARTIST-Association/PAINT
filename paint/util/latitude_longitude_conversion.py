import math
import paint.util.paint_mappings as mappings

def add_offset_to_lat_lon(north_offset_m, east_offset_m):
    """
    Adds an offset to the given latitude and longitude coordinates.

    Args:
        north_offset_m (float): The distance in meters to add to the latitude.
        east_offset_m (float): The distance in meters to add to the longitude.

    Returns:
        tuple: A tuple containing the new latitude and longitude in degrees.
    """
    # Convert latitude and longitude to radians
    lat_rad = math.radians(mappings.POWER_PLANT_LAT)
    lon_rad = math.radians(mappings.POWER_PLANT_LON)

    # Calculate meridional radius of curvature
    sin_lat = math.sin(lat_rad)
    Rn = mappings.WGS84_A / math.sqrt(1 - mappings.WGS84_E2 * sin_lat**2)

    # Calculate transverse radius of curvature
    Rm = (mappings.WGS84_A * (1 - mappings.WGS84_E2)) / ((1 - mappings.WGS84_E2 * sin_lat**2)**1.5)

    # Calculate new latitude
    dlat = north_offset_m / Rm
    new_lat_rad = lat_rad + dlat

    # Calculate new longitude using the original meridional radius of curvature
    dlon = east_offset_m / (Rn * math.cos(lat_rad))
    new_lon_rad = lon_rad + dlon

    # Convert back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon


def calculate_heliostat_position_in_m_from_lat_lon(lat1, lon1, alt):
    """
    Calculate the position of a heliostat in meters from given latitude, longitude, and altitude.

    Args:
        lat1 (float): The latitude of the heliostat in degrees.
        lon1 (float): The longitude of the heliostat in degrees.
        alt (float): The altitude of the heliostat.

    Returns:
        list: A list containing the north offset in meters, east offset in meters, and the altitude difference from the power plant.

    This function calculates the north and east offsets in meters of a heliostat from the power plant location.
    It converts the latitude and longitude to radians, calculates the radius of curvature values,
    and then computes the offsets based on the differences between the heliostat and power plant coordinates.
    Finally, it returns a list containing these offsets along with the altitude difference.
    """
    # Convert latitude and longitude to radians
    lat_heliostat_rad = math.radians(lat1)
    lon_heliostat_rad = math.radians(lon1)
    alt_heliostat = alt - mappings.POWER_PLANT_ALT
    lat_tower_rad = math.radians(mappings.POWER_PLANT_LAT)
    lon_tower_rad = math.radians(mappings.POWER_PLANT_LON)

    # Calculate meridional radius of curvature for the first latitude
    sin_lat1 = math.sin(lat_heliostat_rad)
    Rn1 = mappings.WGS84_A / math.sqrt(1 - mappings.WGS84_E2 * sin_lat1**2)

    # Calculate transverse radius of curvature for the first latitude
    Rm1 = (mappings.WGS84_A * (1 - mappings.WGS84_E2)) / ((1 - mappings.WGS84_E2 * sin_lat1**2)**1.5)

    # Calculate meridional radius of curvature for the second latitude
    sin_lat2 = math.sin(lat_tower_rad)
    Rn2 = mappings.WGS84_A / math.sqrt(1 - mappings.WGS84_E2 * sin_lat2**2)

    # Calculate transverse radius of curvature for the second latitude
    Rm2 = (mappings.WGS84_A * (1 - mappings.WGS84_E2)) / ((1 - mappings.WGS84_E2 * sin_lat2**2)**1.5)

    # Calculate delta latitude and delta longitude in radians
    dlat_rad = lat_tower_rad - lat_heliostat_rad
    dlon_rad = lon_tower_rad - lon_heliostat_rad

    # Calculate north and east offsets in meters
    north_offset_m = dlat_rad * Rm1
    east_offset_m = dlon_rad * Rn1 * math.cos(lat_heliostat_rad)

    return [north_offset_m, east_offset_m, alt_heliostat]
