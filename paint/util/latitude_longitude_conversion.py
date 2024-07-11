import math
import paint.util.paint_mappings as mappings

def add_offset_to_lat_lon(lat, lon, north_offset_m, east_offset_m):
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

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


# Given coordinates
POWER_PLANT_LAT = 50.913296351383806
POWER_PLANT_LON = 6.387514846666862

# Example offsets in meters
north_offset_m = 25
east_offset_m = -30

# Calculate new coordinates
new_lat, new_lon = add_offset_to_lat_lon(POWER_PLANT_LAT, POWER_PLANT_LON, north_offset_m, east_offset_m)
print("New Latitude:", new_lat)
print("New Longitude:", new_lon)
