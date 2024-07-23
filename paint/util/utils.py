import argparse
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


def load_and_format_heliostat_axis_data(arguments: argparse.Namespace) -> pd.DataFrame:
    """
    Prepare the axis csv for concatenation by changing certain column names and rearranging the order.

    Parameters
    ----------
    arguments : argparse.Namespace
        The arguments containing the input and output path.

    Returns
    -------
    pd.DataFrame
        The processed axis dataframe.
    """
    df_axis = pd.read_csv(
        arguments.input_axis,
        header=0,
        decimal=",",
        sep=";",
    )
    pivoted_df = df_axis.pivot(index=mappings.HELIOSTAT_ID, columns="Number")
    # Flatten the multi-index columns
    pivoted_df.columns = [
        "_".join(map(str, col)).strip() for col in pivoted_df.columns.values
    ]

    # Reset index to bring 'HeliostatId' back as a column
    pivoted_df = pivoted_df.reset_index()
    # Rename columns that are always identical
    pivoted_df = pivoted_df.rename(
        columns={
            "FieldId_1": mappings.FIELD_ID,
            "CreatedAt_1": mappings.CREATED_AT,
            "UpdatedAt_1": mappings.UPDATED_AT,
        }
    )
    pivoted_df = pivoted_df.drop(columns=["FieldId_2", "CreatedAt_2", "UpdatedAt_2"])
    pivoted_df.columns = [
        col.replace("_1", "_axis_1").replace("_2", "_axis_2")
        for col in pivoted_df.columns
    ]
    # Get list of columns ending with _axis_1 and _axis_2
    axis_1_columns = [col for col in pivoted_df.columns if col.endswith("_axis_1")]
    axis_2_columns = [col for col in pivoted_df.columns if col.endswith("_axis_2")]

    # Sort the columns list to have _axis_1 columns first, followed by _axis_2 columns
    sorted_columns = axis_1_columns + axis_2_columns

    # Reorder columns in the dataframe
    pivoted_df = pivoted_df[
        [mappings.HELIOSTAT_ID, mappings.FIELD_ID, mappings.CREATED_AT] + sorted_columns
    ]
    pivoted_df.set_index(mappings.HELIOSTAT_ID, inplace=True)
    pivoted_df.index = pivoted_df.index.map(heliostat_id_to_name)
    return pivoted_df


def load_and_format_heliostat_positions(
    arguments: argparse.Namespace,
) -> pd.DataFrame:
    """
    Prepare the heliostat positions csv for concatenation by changing certain column names and rearranging the order.

    Parameters
    ----------
    arguments : argparse.Namespace
        The arguments containing the input and output path.

    Returns
    -------
    pd.DataFrame
        The processed heliostat positions dataframe.
    """
    df_heliostat_positions = pd.read_excel(arguments.input_position, header=0)
    df_heliostat_positions.set_index(mappings.INTERNAL_NAME_INDEX, inplace=True)
    df_heliostat_positions.rename_axis(mappings.HELIOSTAT_ID, inplace=True)
    # Drop the specified columns
    df_heliostat_positions.drop(
        columns=["RowName", "Number", "ColumnName"], inplace=True
    )

    # Rename the columns
    df_heliostat_positions.rename(
        columns={
            "x": mappings.EAST_KEY,
            "y": mappings.NORTH_KEY,
            "z": mappings.ALTITUDE_KEY,
            "Spalte1": mappings.HEIGHT_ABOVE_GROUND,
        },
        inplace=True,
    )

    return df_heliostat_positions


def merge_and_sort_df(
    df_heliostat_positions: pd.DataFrame, df_axis: pd.DataFrame
) -> pd.DataFrame:
    """
    Concatenate the heliostat position and heliostat axis data and sort in the correct order.

    Parameters
    ----------
    df_heliostat_positions : pd.DataFrame
        The dataframe containing the heliostat positions.
    df_axis : pd.DataFrame
        The dataframe containing the heliostat axis data.

    Returns
    -------
    pd.DataFrame
        The concatenated and sorted data frame.
    """
    df_concatenated = pd.concat([df_heliostat_positions, df_axis], axis=1, join="inner")
    created_at = df_concatenated.pop(mappings.CREATED_AT)
    df_concatenated.insert(0, mappings.CREATED_AT, created_at)
    return df_concatenated
