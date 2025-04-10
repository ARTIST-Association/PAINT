#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import paint.util.paint_mappings as mappings
import paint.util.renovation_mappings as renovations
from paint import PAINT_ROOT
from paint.preprocessing.properties_stac import (
    make_properties_collection,
    make_properties_item,
)
from paint.util.preprocessing import (
    load_and_format_heliostat_axis_data,
    load_and_format_heliostat_positions,
    merge_and_sort_df,
)
from paint.util.utils import (
    to_utc_single,
)


def extract_properties_data_and_generate_stac_item(
    arguments: argparse.Namespace,
    heliostat_id: str,
    heliostat_data: pd.Series,
    renovation_data: pd.Series,
    facet_data: dict[str, Any],
) -> tuple[float, float]:
    """
    Extract the properties data and generate associated STAC items.

    This function extracts the properties data for a given heliostat, saves this data as a json file, and also generates
    the associated STAC item.

    Parameters
    ----------
    arguments : argparse.Namespace
        Command-line arguments.
    heliostat_id : str
        ID of the heliostat considered.
    heliostat_data : pd.Series
        Data for the heliostat.
    renovation_data : pd.Series
        Data for the renovations.
    facet_data : dict[str, Any]
        Data for the facets.

    Returns
    -------
    float
        Latitude coordinate of the heliostat.
    float
        Longitude coordinate of the heliostat.
    """
    # Generate properties STAC.
    lat_lon, properties_stac = make_properties_item(
        heliostat_key=heliostat_id,
        heliostat_data=heliostat_data,
    )

    # Save properties STAC.
    save_properties_stac_path = (
        Path(arguments.output_path)
        / heliostat_id
        / mappings.SAVE_PROPERTIES
        / (mappings.HELIOSTAT_PROPERTIES_ITEM % heliostat_id)
    )
    save_properties_stac_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_properties_stac_path, mode="w") as handle:
        json.dump(properties_stac, handle)

    # Convert kinematic data to dict and remove metadata.
    kinematic_helper_data = heliostat_data.to_dict()
    for key_to_remove in [
        mappings.CREATED_AT,
        mappings.EAST_KEY,
        mappings.NORTH_KEY,
        mappings.ALTITUDE_KEY,
        mappings.FIELD_ID,
    ]:
        kinematic_helper_data.pop(key_to_remove, None)

    # Only consider data for the first actuator.
    actuator_1_data = {
        key: value for key, value in kinematic_helper_data.items() if key.endswith("_1")
    }
    # Map to appropriate names.
    actuator_1_data = {
        mappings.HELIOSTAT_PROPERTIES_CONVERSION_MAP[key.rsplit("_", 1)[0]]: (
            value.lower() if isinstance(value, str) else value
        )
        for key, value in actuator_1_data.items()
        if key.rsplit("_", 1)[0]
        in mappings.HELIOSTAT_PROPERTIES_CONVERSION_MAP  # Ensure the base key exists in the mapping
    }

    # Now consider data for the second actuator.
    actuator_2_data = {
        key: value for key, value in kinematic_helper_data.items() if key.endswith("_2")
    }
    # Also map to the appropriate names here.
    actuator_2_data = {
        mappings.HELIOSTAT_PROPERTIES_CONVERSION_MAP[key.rsplit("_", 1)[0]]: (
            value.lower() if isinstance(value, str) else value
        )
        for key, value in actuator_2_data.items()
        if key.rsplit("_", 1)[0]
        in mappings.HELIOSTAT_PROPERTIES_CONVERSION_MAP  # Ensure the base key exists in the mapping
    }

    # Include all kinematic data.
    kinematic_data = {
        mappings.ACTUATOR_KEY: [actuator_1_data, actuator_2_data],
        mappings.FIRST_JOINT_TRANSLATION_E_KEY: mappings.FIRST_JOINT_TRANSLATION_E,
        mappings.FIRST_JOINT_TRANSLATION_N_KEY: mappings.FIRST_JOINT_TRANSLATION_N,
        mappings.FIRST_JOINT_TRANSLATION_U_KEY: mappings.FIRST_JOINT_TRANSLATION_U,
        mappings.SECOND_JOINT_TRANSLATION_E_KEY: mappings.SECOND_JOINT_TRANSLATION_E,
        mappings.SECOND_JOINT_TRANSLATION_N_KEY: mappings.SECOND_JOINT_TRANSLATION_N,
        mappings.SECOND_JOINT_TRANSLATION_U_KEY: mappings.SECOND_JOINT_TRANSLATION_U,
        mappings.CONCENTRATOR_TRANSLATION_E_KEY: mappings.CONCENTRATOR_TRANSLATION_E,
        mappings.CONCENTRATOR_TRANSLATION_N_KEY: mappings.CONCENTRATOR_TRANSLATION_N,
        mappings.CONCENTRATOR_TRANSLATION_U_KEY: mappings.CONCENTRATOR_TRANSLATION_U,
    }

    # Extract renovation date.
    renovation_date = renovations.renovation_number_to_date[
        renovation_data[mappings.RENOVATION_ID]
    ]
    if renovation_date is mappings.RENOVATION_ERROR:
        raise ValueError(f"Renovation data is missing for {heliostat_id}!")

    # Extract facets data.
    facets_dict = {
        mappings.CANTING_TYPE: mappings.MAP_CANTING_TO_READABLE[
            facet_data[mappings.CANTING_KEY]
        ],
        mappings.NUM_FACETS: mappings.FOUR_FACETS,
        mappings.FACETS_LIST: [
            {
                mappings.TRANSLATION_VECTOR: mappings.FACET_1_TRANSLATION,
                mappings.CANTING_E: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_E], mappings.FACET_1_ROTATION_E
                    )
                ],
                mappings.CANTING_N: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_N], mappings.FACET_1_ROTATION_N
                    )
                ],
            },
            {
                mappings.TRANSLATION_VECTOR: mappings.FACET_2_TRANSLATION,
                mappings.CANTING_E: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_E], mappings.FACET_2_ROTATION_E
                    )
                ],
                mappings.CANTING_N: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_N], mappings.FACET_2_ROTATION_N
                    )
                ],
            },
            {
                mappings.TRANSLATION_VECTOR: mappings.FACET_3_TRANSLATION,
                mappings.CANTING_E: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_E], mappings.FACET_3_ROTATION_E
                    )
                ],
                mappings.CANTING_N: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_N], mappings.FACET_3_ROTATION_N
                    )
                ],
            },
            {
                mappings.TRANSLATION_VECTOR: mappings.FACET_4_TRANSLATION,
                mappings.CANTING_E: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_E], mappings.FACET_4_ROTATION_E
                    )
                ],
                mappings.CANTING_N: [
                    a * b
                    for a, b in zip(
                        facet_data[mappings.SPAN_N], mappings.FACET_4_ROTATION_N
                    )
                ],
            },
        ],
    }
    # Save all data in properties dictionary.
    properties_data = {
        mappings.HELIOSTAT_POSITION_KEY: [
            lat_lon[0],
            lat_lon[1],
            heliostat_data[mappings.ALTITUDE_KEY],
        ],
        mappings.HELIOSTAT_HEIGHT_KEY: mappings.HELIOSTAT_HEIGHT,
        mappings.HELIOSTAT_WIDTH_KEY: mappings.HELIOSTAT_WIDTH,
        mappings.INITIAL_ORIENTATION_KEY: mappings.INITIAL_ORIENTATION_VALUE,
        mappings.KINEMATIC_PROPERTIES_KEY: kinematic_data,
        mappings.FACET_PROPERTIES_KEY: facets_dict,
        mappings.RENOVATION_PROPERTIES_KEY: renovation_date,
    }

    # Save properties data.
    save_properties_path = (
        Path(arguments.output_path)
        / heliostat_id
        / mappings.SAVE_PROPERTIES
        / (mappings.HELIOSTAT_PROPERTIES_SAVE_NAME % heliostat_id)
    )
    save_properties_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_properties_path, mode="w") as file:
        json.dump(properties_data, file)

    return lat_lon


def main(arguments: argparse.Namespace):
    """
    Generate kinematic properties STAC items and save raw data.

    This function extracts the kinematic properties data for each heliostat and saves this as a json file. Additionally,
    the STAC items for each of these files are automatically generated.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    # Check if saved metadata exists and load if required.
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
    # Load heliostat position and axis data and reformat for easy parsing.
    df_heliostat_positions = load_and_format_heliostat_positions(arguments)
    df_axis = load_and_format_heliostat_axis_data(arguments)
    df_concatenated = merge_and_sort_df(df_heliostat_positions, df_axis)

    # Load renovation data.
    df_renovations = pd.read_csv(arguments.input_renovations)
    df_renovations.index = df_renovations[mappings.INTERNAL_NAME_INDEX]

    # Load facet data.
    facet_dict = np.load(arguments.input_facets, allow_pickle=True).item()

    # Extract kinematic properties data and STAC.
    for key, data in df_concatenated.iterrows():
        assert isinstance(key, str)

        lat_lon = extract_properties_data_and_generate_stac_item(
            arguments=arguments,
            heliostat_id=key,
            heliostat_data=data,
            renovation_data=df_renovations.loc[key],
            facet_data=facet_dict[key],
        )

        url = mappings.HELIOSTAT_PROPERTIES_ITEM_URL % (key, key)
        properties_items.loc[0] = [
            key,
            f"heliostat properties for {key}",
            url,
            to_utc_single(data[mappings.CREATED_AT]),
            lat_lon[0],
            lat_lon[1],
            data[mappings.ALTITUDE_KEY],
        ]

        collection = make_properties_collection(heliostat_id=key, data=properties_items)
        save_path = (
            Path(arguments.output_path)
            / key
            / mappings.SAVE_PROPERTIES
            / (mappings.HELIOSTAT_PROPERTIES_COLLECTION_FILE % key)
        )
        save_path.parent.mkdir(exist_ok=True, parents=True)
        with open(save_path, "w") as out:
            json.dump(collection, out)


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    input_axis = Path(lsdf_root) / "paint" / "PAINT" / "axis_data.csv"
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_position = Path(lsdf_root) / "paint" / "PAINT" / "heliostat_positions.csv"
    input_renovations = Path(lsdf_root) / "paint" / "PAINT" / "renovation_data.csv"
    input_facets = Path(lsdf_root) / "paint" / "PAINT" / "facet_data.npy"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_position",
        type=Path,
        help="Path to the heliostat position input file",
        default=str(input_position),
    )
    parser.add_argument(
        "--input_axis",
        type=Path,
        help="Path to the axis data input file",
        default=str(input_axis),
    )
    parser.add_argument(
        "--input_renovations",
        type=Path,
        help="Path to the renovations data input file",
        default=str(input_renovations),
    )
    parser.add_argument(
        "--input_facets",
        type=Path,
        help="Path to the facet data input file",
        default=str(input_facets),
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
        default=str(output_folder),
    )
    args = parser.parse_args()
    main(arguments=args)
