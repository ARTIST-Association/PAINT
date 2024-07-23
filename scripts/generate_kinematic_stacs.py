#!/usr/bin/env python

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.kinematic_stac import make_kinematic_item
from paint.util.utils import (
    load_and_format_heliostat_axis_data,
    load_and_format_heliostat_positions,
    merge_and_sort_df,
    to_utc_single,
)


def extract_kinematic_data_and_generate_stacs(
    arguments: argparse.Namespace,
    heliostat_id: str,
    kinematic_data: pd.Series,
    properties_items: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract the kinematic data and generate associated stac items.

    This function extracts the kinematic data for a given heliostat, saves this data as a json file, and also generates
    the associated stac item.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    heliostat_id : str
        The id of the heliostat considered.
    kinematic_data : pd.Series
        The kinematic data for the heliostat.
    properties_items : pd.DataFrame
        The dataframe containing the metadata for each heliostat property to be used for collection creation later.

    Returns
    -------
    pd.DataFrame
        The dataframe containing the metadata for each heliostat property to be used for collection creation later.
    """
    lat_lon, kinematic_stac = make_kinematic_item(
        heliostat_key=heliostat_id, heliostat_data=kinematic_data
    )

    # save item metadata for collection creation later
    url = mappings.KINEMATIC_PROPERTIES_ITEM_URL % heliostat_id
    properties_items.loc[len(properties_items)] = [
        heliostat_id,
        f"kinematic properties for {heliostat_id}",
        url,
        to_utc_single(kinematic_data[mappings.CREATED_AT]),
        lat_lon[0],
        lat_lon[1],
        kinematic_data[mappings.ALTITUDE_KEY],
    ]

    # save kinematic properties STAC
    save_kinematic_stac_path = (
        Path(arguments.output_path)
        / heliostat_id
        / mappings.SAVE_PROPERTIES
        / (mappings.KINEMATIC_PROPERTIES_ITEM % heliostat_id)
    )
    save_kinematic_stac_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_kinematic_stac_path, mode="w") as handle:
        json.dump(kinematic_stac, handle)

    # convert kinematic data to dict and remove metadata
    dict_data = kinematic_data.to_dict()
    for key_to_remove in [
        mappings.CREATED_AT,
        mappings.EAST_KEY,
        mappings.NORTH_KEY,
        mappings.ALTITUDE_KEY,
        mappings.FIELD_ID,
        mappings.HEIGHT_ABOVE_GROUND,
    ]:
        dict_data.pop(key_to_remove, None)

    # save kinematic properties measurements
    save_kinematic_properties_path = (
        Path(arguments.output_path)
        / heliostat_id
        / mappings.SAVE_PROPERTIES
        / (heliostat_id + mappings.KINEMATIC_PROPERTIES_SUFFIX)
    )
    save_kinematic_properties_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_kinematic_properties_path, mode="w") as handle:
        json.dump(dict_data, handle)
    return properties_items


def main(arguments: argparse.Namespace):
    """
    Generate kinematic properties stac items and save raw data.

    This function extracts the kinematic properties data for each heliostat and saves this as a json file. Additionally,
    the stac items for each of these files are automatically generated. Finally, the metadata for each of these stac
    items is saved for collection creation later.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    # check if saved metadata exists and load if required
    properties_items_path = Path(f"{PAINT_ROOT}/TEMPDATA/properties_items.csv")
    if properties_items_path.exists():
        properties_items = pd.read_csv(properties_items_path)
    else:
        properties_items_path.parent.mkdir(parents=True, exist_ok=True)
        properties_items = pd.DataFrame(
            columns=[
                mappings.HELIOSTAT_ID,
                mappings.TITLE_KEY,
                mappings.URL_KEY,
                mappings.CREATED_AT,
                mappings.LATITUDE_KEY,
                mappings.LONGITUDE_KEY,
                mappings.ELEVATION,
            ]
        )

    # load heliostat position and axis data and reformat for easy parsing
    df_heliostat_positions = load_and_format_heliostat_positions(arguments)
    df_axis = load_and_format_heliostat_axis_data(arguments)
    df_concatenated = merge_and_sort_df(df_heliostat_positions, df_axis)

    # extract kinematic properties data and STAC
    for key, data in df_concatenated.iterrows():
        assert isinstance(key, str)
        properties_items = extract_kinematic_data_and_generate_stacs(
            arguments=arguments,
            heliostat_id=key,
            kinematic_data=data,
            properties_items=properties_items,
        )

    properties_items.to_csv(properties_items_path, index=False)


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "generate_deflectometry_and_facet_stacs.py",
        "--input_position",
        f"{PAINT_ROOT}/ExampleDataKIT/Heliostatpositionen_xyz.xlsx",
        "--input_axis",
        f"{PAINT_ROOT}/ExampleDataKIT/axis_data.csv",
        "--output_path",
        f"{PAINT_ROOT}/ConvertedData",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_position",
        type=Path,
        help="Path to the heliostat position input file",
    )
    parser.add_argument(
        "--input_axis",
        type=Path,
        help="Path to the axis data input file",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    args = parser.parse_args()
    main(arguments=args)
