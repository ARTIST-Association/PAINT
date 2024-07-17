from datetime import datetime
from typing import Tuple, Union

import numpy as np
import pandas as pd
import pytz
from dateutil import parser

import paint.util.paint_mappings as mappings


def calculate_azimuth_and_elevation(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
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
    # extract sun positions in each coordinate
    sun_position_east = np.array(df[mappings.SUN_POSITION_EAST])
    sun_position_north = -np.array(df[mappings.SUN_POSITION_NORTH])
    sun_position_up = np.array(df[mappings.SUN_POSITION_UP])

    # calculate azimuth and evaluation and return.
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


def to_utc_single(datetime_str: str, local_tz: str = "Europe/Berlin") -> str:
    """
    Parse a local datetime string and convert to UTC.

    Parameters
    ----------
    datetime_str : str
        The string containing the local datetime in the format 'YYMMDDHHMMSS'.
    local_tz : str
        The local timezone (Default: 'Europe/Berlin').

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

    # Return the UTC datetime as a string
    return utc_time.strftime(mappings.TIME_FORMAT)
