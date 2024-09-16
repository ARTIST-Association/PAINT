#!/usr/bin/env python

import argparse
import json
from pathlib import Path
from typing import Tuple

import pandas as pd

import paint.util.paint_mappings as mappings
import paint.util.renovation_mappings as renovations
from paint import PAINT_ROOT
from paint.data.properties_stac import make_properties_collection, make_properties_item
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
) -> Tuple[float, float]:
    """
    Extract the properties data and generate associated stac items.

    This function extracts the properties data for a given heliostat, saves this data as a json file, and also generates
    the associated stac item.

    Parameters
    ----------
    arguments : argparse.Namespace
        Command line arguments.
    heliostat_id : str
        ID of the heliostat considered.
    heliostat_data : pd.Series
        Data for the heliostat.
    renovation_data : pd.Series
        Data for the renovations.

    Returns
    -------
    float
        Latitude coordinate of the heliostat.
    float
        Longitude coordinate of the heliostat.
    """
    # Generate properties STAC.
    lat_lon, properties_stac = make_properties_item(
        heliostat_key=heliostat_id, heliostat_data=heliostat_data
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
    kinematic_data = heliostat_data.to_dict()
    for key_to_remove in [
        mappings.CREATED_AT,
        mappings.EAST_KEY,
        mappings.NORTH_KEY,
        mappings.ALTITUDE_KEY,
        mappings.FIELD_ID,
        mappings.HEIGHT_ABOVE_GROUND,
    ]:
        kinematic_data.pop(key_to_remove, None)

    # Extract renovation date.
    renovation_date = renovations.renovation_number_to_date[
        renovation_data[mappings.RENOVATION_ID]
    ]
    if renovation_date is mappings.RENOVATION_ERROR:
        raise ValueError(f"Renovation data is missing for {heliostat_id}!")

    # Save all data in properties dictionary.
    properties_data = {
        mappings.HELIOSTAT_POSITION_KEY: [
            lat_lon[0],
            lat_lon[1],
            heliostat_data[mappings.ALTITUDE_KEY],
        ],
        mappings.KINEMATIC_PROPERTIES_KEY: kinematic_data,
        mappings.FACET_PROPERTIES_KEY: {},
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

    df_renovations = pd.read_csv(arguments.input_renovations)
    df_renovations.index = df_renovations[mappings.INTERNAL_NAME_INDEX]

    # extract kinematic properties data and STAC
    for key, data in df_concatenated.iterrows():
        assert isinstance(key, str)

        lat_lon = extract_properties_data_and_generate_stac_item(
            arguments=arguments,
            heliostat_id=key,
            heliostat_data=data,
            renovation_data=df_renovations.loc[key],
        )

        # Save item metadata for collection creation later.
        url = mappings.HELIOSTAT_PROPERTIES_ITEM_URL % (key, key)
        properties_items.loc[len(properties_items)] = [
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
    # lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    # input_axis = Path(lsdf_root) / "paint" / "PAINT" / "axis_data.csv"
    # output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    # input_position = (
    #     Path(lsdf_root) / "paint" / "PAINT" / "Heliostatpositionen_xyz.xlsx"
    # )
    # input_renovations = (
    #         Path(lsdf_root) / "paint" / "PAINT" / "renovation_data.csv"
    # )

    input_axis = Path(PAINT_ROOT) / "ExampleDataKIT" / "axis_data.csv"
    output_folder = Path(PAINT_ROOT) / "ATA"
    input_position = (
        Path(PAINT_ROOT) / "ExampleDataKIT" / "Heliostatpositionen_xyz.xlsx"
    )
    input_renovations = Path(PAINT_ROOT) / "ExampleDataKIT" / "renovation_data.csv"

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
        "--output_path",
        type=Path,
        help="Path to save the output files",
        default=str(output_folder),
    )
    args = parser.parse_args()
    main(arguments=args)


# #
# # # Extract facet properties data and save.
# # saved_facet_path = (
# #         Path(self.output_path)
# #         / self.heliostat_id
# #         / mappings.SAVE_PROPERTIES
# #         / self.json_handle
# # )
# # saved_facet_path.parent.mkdir(parents=True, exist_ok=True)
# # if self.raw_data:
# #     with open(saved_facet_path, "w") as handle:
# #         properties = {
# #             mappings.NUM_FACETS: number_of_facets,
# #             mappings.FACETS_LIST: [
# #                 {
# #                     mappings.TRANSLATION_VECTOR: facet_translation_vectors[
# #                                                  i, :
# #                                                  ].tolist(),
# #                     mappings.CANTING_E: canting_e[i, :].tolist(),
# #                     mappings.CANTING_N: canting_n[i, :].tolist(),
# #                 }
# #                 for i in range(number_of_facets)
# #             ],
# #         }
# #         json.dump(properties, handle)
