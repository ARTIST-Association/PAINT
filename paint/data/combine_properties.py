#!/usr/bin/env python

import argparse
import json
import pathlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import heliostat_id_to_name


def prepare_axis_file_for_concatenation(arguments: argparse.Namespace) -> pd.DataFrame:
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


def prepare_heliostat_positions_for_concatenation(
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


def create_heliostat_properties_json(arguments: argparse.Namespace) -> None:
    """
    Combine multiple CSV files and a json file and save these as a heliostat properties json.

    Parameters
    ----------
    arguments : argparse.Namespace
        The arguments containing the input and output path.
    """
    # ensure that the output paths exist
    arguments.output.mkdir(parents=True, exist_ok=True)

    df_heliostat_positions = prepare_heliostat_positions_for_concatenation(arguments)
    df_axis = prepare_axis_file_for_concatenation(arguments)
    df_concatenated = merge_and_sort_df(df_heliostat_positions, df_axis)

    metadata_df = pd.DataFrame(
        columns=[
            mappings.DEFLECTOMETRY_CREATED_AT,
            mappings.CREATED_AT,
            mappings.EAST_KEY,
            mappings.NORTH_KEY,
            mappings.ALTITUDE_KEY,
            mappings.HEIGHT_ABOVE_GROUND,
        ],
        index=df_concatenated.index,
    )
    # add facet data and save file
    for key, data in df_concatenated.iterrows():
        assert isinstance(key, str)
        metadata = data[
            [
                mappings.CREATED_AT,
                mappings.EAST_KEY,
                mappings.NORTH_KEY,
                mappings.ALTITUDE_KEY,
                mappings.HEIGHT_ABOVE_GROUND,
            ]
        ].values

        # convert kinematic data to dict and remove metadata
        dict_data = data.to_dict()
        for key_to_remove in [
            mappings.CREATED_AT,
            mappings.EAST_KEY,
            mappings.NORTH_KEY,
            mappings.ALTITUDE_KEY,
            mappings.DEFLECTOMETRY_CREATED_AT,
            mappings.FIELD_ID,
            mappings.HEIGHT_ABOVE_GROUND,
        ]:
            dict_data.pop(key_to_remove, None)

        full_data = {mappings.KINEMATIC_KEY: dict_data}
        # load facet data
        facet_file_name = Path(key + mappings.PROPERTIES_SUFFIX)
        full_facet_path = arguments.input_facet_root / facet_file_name
        if full_facet_path.is_file():
            with open(full_facet_path, "r") as file:
                facet_data = json.load(file)

            metadata = np.insert(
                metadata, 0, facet_data.pop(mappings.DEFLECTOMETRY_CREATED_AT)
            )
            full_data.update(facet_data)
        else:
            metadata = np.insert(metadata, 0, np.NAN)

        metadata_df.loc[key] = metadata
        file_name = Path(key + mappings.PROPERTIES_SUFFIX)
        with open(arguments.output / file_name, "w") as handle:
            json.dump(full_data, handle)

    metadata_df.to_csv(arguments.output / "heliostat_metadata.csv")


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "heliostat_properties_stac.py",
        "-i_position",
        f"{PAINT_ROOT}/ExampleDataKIT/Heliostatpositionen_xyz.xlsx",
        "-i_axis",
        f"{PAINT_ROOT}/ExampleDataKIT/axis_data.csv",
        "-i_root",
        f"{PAINT_ROOT}/ConvertedData",
        "-o",
        f"{PAINT_ROOT}/ConvertedData/NewProperties",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i_position",
        "--input_position",
        type=pathlib.Path,
        help="Path to the heliostat position input file",
    )
    parser.add_argument(
        "-i_axis",
        "--input_axis",
        type=pathlib.Path,
        help="Path to the axis data input file",
    )
    parser.add_argument(
        "-i_root",
        "--input_facet_root",
        type=pathlib.Path,
        help="Path to the root directory for loading facet properties",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default="stac",
        help="Path to the output file",
    )
    args = parser.parse_args()

    create_heliostat_properties_json(args)