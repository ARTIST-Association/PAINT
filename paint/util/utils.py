import math
from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd
import pytz
from dateutil import parser

import paint.util.paint_mappings as mappings


def calculate_azimuth_and_elevation(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate the azimuth and elevation given sun positions.

    Parameters
    ----------
    df : pd.DataFrame
        The pandas dataframe containing the sun positions.

    Returns
    -------
    np.ndarray
        The calculated azimuth in degrees.
    np.ndarray
        The calculated elevation in degrees.
    """
    # Extract sun positions in each coordinate.
    sun_position_east = np.array(df[mappings.SUN_POSITION_EAST])
    sun_position_north = -np.array(df[mappings.SUN_POSITION_NORTH])
    sun_position_up = np.array(df[mappings.SUN_POSITION_UP])

    # Calculate azimuth and evaluation and return.
    azimuth_degree = np.degrees(np.arctan2(sun_position_east, sun_position_north))
    elevation_degree = np.degrees(
        np.arctan2(
            sun_position_up, np.sqrt(sun_position_east**2 + sun_position_north**2)
        )
    )

    return azimuth_degree, elevation_degree


def heliostat_id_to_name(heliostat_id: Union[int, str]) -> str:
    """
    Convert a heliostat id to its name.

    Parameters
    ----------
    heliostat_id : Union[int, str]
        The heliostat ID to be converted.

    Returns
    -------
    str
        The heliostat name derived from the heliostat ID.
    """
    str_ = str(heliostat_id)
    return "".join(
        [chr(ord("A") + int(str_[0]) - 1), chr(ord("A") + int(str_[1:3]) - 1), str_[3:]]
    )


def to_utc(time_series: pd.Series) -> pd.Series:
    """
    Parse local datetime strings and convert to UTC.

    Parameters
    ----------
    time_series : pd.Series
        The series containing the local datetime strings.

    Returns
    -------
    pd.Series
        The corresponding UTC datetime objects.
    """
    return (
        pd.to_datetime(time_series)
        .dt.tz_localize("Europe/Berlin", ambiguous="infer")
        .dt.tz_convert("UTC")
    )


def to_utc_single(
    datetime_str: str, local_tz: str = "Europe/Berlin", file_name_format: bool = False
) -> str:
    """
    Parse a single local datetime string and convert to UTC.

    Parameters
    ----------
    datetime_str : str
        String containing the local datetime.
    local_tz : str
        Local timezone (Default: ``Europe/Berlin``).
    file_name_format : bool
        Indicating whether the file name format for the time conversion should be used or not (Default: ``False``).

    Returns
    -------
    str
        The corresponding UTC datetime string.
    """
    try:
        # Try parsing with dateutil.parser for general datetime strings
        local_time = parser.parse(datetime_str)
    except ValueError:
        try:
            # Fall back to manual parsing for specific format "%y%m%d%H%M%S"
            local_time = datetime.strptime(datetime_str, "%y%m%d%H%M%S")
        except ValueError as e:
            raise ValueError(f"Unable to parse datetime string: {datetime_str}") from e

    # Localize the datetime object to the specified local timezone
    local_tz_obj = pytz.timezone(local_tz)
    if local_time.tzinfo is None:
        local_time = local_tz_obj.localize(local_time, is_dst=None)

    # Convert the localized datetime to UTC
    utc_time = local_time.astimezone(pytz.utc)

    # Convert the time to the appropriate string.
    if file_name_format:
        return_string = utc_time.strftime(mappings.TIME_FILE_FORMAT)
    else:
        return_string = utc_time.strftime(mappings.TIME_FORMAT)

    return return_string


def convert_field_coordinate_to_wgs84(
    east_coordinate_m: float,
    north_coordinate_m: float,
) -> tuple[float, float]:
    """
    Convert field coordinates (East, North) to WGS84 (latitude, longitude) coordinates.

    Parameters
    ----------
    east_coordinate_m : float
        Field coordinate in the east direction in meters.
    north_coordinate_m : float
        Field coordinate in the north direction in meters.

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
    dlat = north_coordinate_m / rm
    new_lat_rad = lat_rad + dlat

    # Calculate new longitude using the original meridional radius of curvature
    dlon = east_coordinate_m / (rn * math.cos(lat_rad))
    new_lon_rad = lon_rad + dlon

    # Convert back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon
