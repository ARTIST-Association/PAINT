import argparse

import pandas as pd

from paint.util import paint_mappings as mappings
from paint.util.utils import heliostat_id_to_name


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
    df_axis = pd.read_csv(arguments.input_axis)
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

    # Fix date time format
    pivoted_df[mappings.CREATED_AT] = pd.to_datetime(
        pivoted_df[mappings.CREATED_AT], dayfirst=True
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
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
    df_heliostat_positions = pd.read_csv(arguments.input_position)
    df_heliostat_positions.set_index(mappings.HELIOSTAT_ID, inplace=True)
    df_heliostat_positions.drop(columns=["id", "FieldId"], inplace=True)
    df_heliostat_positions.rename(
        columns={
            "x": mappings.EAST_KEY,
            "y": mappings.NORTH_KEY,
            "z": mappings.ALTITUDE_KEY,
        },
        inplace=True,
    )
    df_heliostat_positions.index = df_heliostat_positions.index.map(
        heliostat_id_to_name
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
        The concatenated and sorted dataframe.
    """
    df_concatenated = pd.concat([df_heliostat_positions, df_axis], axis=1, join="inner")
    created_at = df_concatenated.pop(mappings.CREATED_AT)
    df_concatenated.insert(0, mappings.CREATED_AT, created_at)
    return df_concatenated
