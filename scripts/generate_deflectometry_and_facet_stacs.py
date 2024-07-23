#!/usr/bin/env python

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Tuple

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.binary_extractor import BinaryExtractor
from paint.data.deflectometry_stac import (
    make_deflectometry_item,
    make_deflectometry_results_item,
)
from paint.data.facet_stac import make_facet_item
from paint.util.utils import load_and_format_heliostat_positions


def extract_data_and_generate_stacs(
    arguments: argparse.Namespace,
    input_path: Path,
    df_heliostat_positions: pd.DataFrame,
    deflectometry_items: pd.DataFrame,
    properties_items: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract the binary data and generate STACS.

    This function extracts the binary data from the ``.binp`` file. After this data is extracted, it also generates
    the STAC items for the deflectometry measurement and the heliostat facet properties. Additionally, it collects the
    summary PDFs for the deflectometry measurement, renames them, copies them to the appropriate location and generates
    a STAC for this PDF.

    Parameters
    ----------
    arguments : argparse.Namespace
        Arguments passed from the command line.
    input_path : pathlib.Path
        Path to the ``.binp`` file.
    df_heliostat_positions : pd.DataFrame
        A dataframe containing information on the heliostat positions.
    deflectometry_items : pd.DataFrame
        A dataframe containing the metadata for all items in the deflectometry collection.
    properties_items : pd.DataFrame
        A dataframe containing the metadata for all items in the heliostat properties collection.

    Returns
    -------
    pd.DataFrame:
        A dataframe containing the metadata for all items in the deflectometry collection.
    pd.DataFrame:
        A dataframe containing the metadata for all items in the heliostat properties collection.
    """
    # Extract binary data
    converter = BinaryExtractor(
        input_path=input_path,
        output_path=arguments.output_path,
        surface_header_name=arguments.surface_header_name,
        facet_header_name=arguments.facet_header_name,
        points_on_facet_struct_name=arguments.points_on_facet_struct_name,
    )
    converter.convert_to_h5_and_extract_properties()
    metadata = df_heliostat_positions.loc[converter.heliostat_id][
        [
            mappings.EAST_KEY,
            mappings.NORTH_KEY,
            mappings.ALTITUDE_KEY,
            mappings.HEIGHT_ABOVE_GROUND,
        ]
    ]
    metadata[mappings.CREATED_AT] = converter.deflectometry_created_at

    # for the raw deflectometry measurements
    if converter.raw_data:
        # create stac and extract latitude and longitude
        lat_lon, stac_item = make_deflectometry_item(
            heliostat_key=converter.heliostat_id,
            heliostat_data=metadata,
            raw_data=True,
        )
        # save item metadata for collection creation later
        url = mappings.DEFLECTOMETRY_RAW_ITEM_URL % (
            converter.heliostat_id,
            converter.deflectometry_created_at,
        )
        deflectometry_items.loc[len(deflectometry_items)] = [
            converter.heliostat_id,
            f"raw deflectometry measurements for {converter.heliostat_id} at {converter.deflectometry_created_at}",
            url,
            converter.deflectometry_created_at,
            lat_lon[0],
            lat_lon[1],
            metadata[mappings.ALTITUDE_KEY],
        ]

        # save the raw deflectometry measurement stac
        save_deflectometry_path = (
            Path(arguments.output_path)
            / converter.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / (
                mappings.DEFLECTOMETRY_RAW_ITEM
                % (converter.heliostat_id, converter.deflectometry_created_at)
            )
        )
        save_deflectometry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_deflectometry_path, mode="w") as handle:
            json.dump(stac_item, handle)

        # extract the facet properties item STAC
        facet_stac = make_facet_item(
            heliostat_key=converter.heliostat_id, heliostat_data=metadata
        )

        # save the facet properties metadata for collection creation later
        facet_url = mappings.FACET_PROPERTIES_ITEM_ITEM_URL % converter.heliostat_id
        properties_items.loc[len(properties_items)] = [
            converter.heliostat_id,
            f"facet properties for {converter.heliostat_id}",
            facet_url,
            converter.deflectometry_created_at,
            lat_lon[0],
            lat_lon[1],
            metadata[mappings.ALTITUDE_KEY],
        ]

        # save facet properties STAC
        save_facet_path = (
            Path(arguments.output_path)
            / converter.heliostat_id
            / mappings.SAVE_PROPERTIES
            / (mappings.FACET_PROPERTIES_ITEM % converter.heliostat_id)
        )
        save_facet_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_facet_path, mode="w") as handle:
            json.dump(facet_stac, handle)

        # find the associated PDF deflectometry results summary and copy it to the correct location with
        # the correct name
        split_name = input_path.name.split("_")
        pdf_name = (
            "_".join(split_name[0:3])
            + "_Result_"
            + split_name[-1].split(".")[0]
            + ".pdf"
        )
        new_pdf_name = (
            Path(arguments.output_path)
            / converter.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / (
                mappings.DEFLECTOMETRY_PDF_NAME
                % (converter.heliostat_id, converter.deflectometry_created_at)
            )
        )
        shutil.copy2(input_path.parent / pdf_name, new_pdf_name)

        # create a STAC for the result PDF
        deflectometry_results_stac_item = make_deflectometry_results_item(
            heliostat_key=converter.heliostat_id, heliostat_data=metadata
        )

        # save the metadata for the result PDF for collection creation later
        result_url = mappings.DEFLECTOMETRY_RESULT_ITEM_URL % (
            converter.heliostat_id,
            converter.deflectometry_created_at,
        )
        deflectometry_items.loc[len(deflectometry_items)] = [
            converter.heliostat_id,
            f"deflectometry results for {converter.heliostat_id} at {converter.deflectometry_created_at}",
            result_url,
            converter.deflectometry_created_at,
            lat_lon[0],
            lat_lon[1],
            metadata[mappings.ALTITUDE_KEY],
        ]

        # save the deflectometry result STAC
        save_deflectometry_results_path = (
            Path(arguments.output_path)
            / converter.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / (
                mappings.DEFLECTOMETRY_RESULT_ITEM
                % (converter.heliostat_id, converter.deflectometry_created_at)
            )
        )
        save_deflectometry_results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_deflectometry_results_path, mode="w") as handle:
            json.dump(deflectometry_results_stac_item, handle)

    else:  # For filled data
        # create stac and extract latitude and longitude
        lat_lon, stac_item = make_deflectometry_item(
            heliostat_key=converter.heliostat_id,
            heliostat_data=metadata,
            raw_data=False,
        )

        # save item metadata for collection creation later
        url = mappings.DEFLECTOMETRY_FILLED_ITEM_URL % (
            converter.heliostat_id,
            converter.deflectometry_created_at,
        )
        deflectometry_items.loc[len(deflectometry_items)] = [
            converter.heliostat_id,
            f"filled deflectometry measurements for {converter.heliostat_id} at {converter.deflectometry_created_at}",
            url,
            converter.deflectometry_created_at,
            lat_lon[0],
            lat_lon[1],
            metadata[mappings.ALTITUDE_KEY],
        ]

        # save the filled deflectometry measurement
        save_deflectometry_path = (
            Path(arguments.output_path)
            / converter.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / (
                mappings.DEFLECTOMETRY_FILLED_ITEM
                % (converter.heliostat_id, converter.deflectometry_created_at)
            )
        )
        save_deflectometry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_deflectometry_path, mode="w") as handle:
            json.dump(stac_item, handle)

    return deflectometry_items, properties_items


def main(arguments: argparse.Namespace):
    """
    Generate deflectometry and facet item STACS.

    This function converts binary data to HDF5 for deflectometry measurements and JSON for facet properties.
    Additionally, the deflectometry results summary PDF is moved to the correct location and renamed. Also, the STAC
    items for deflectometry measurements and facet properties are created. Finally, the metadata for all STAC items is
    saved for collection creation later.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    # check if saved metadata exists and load if required
    deflectometry_items_path = Path(f"{PAINT_ROOT}/TEMPDATA/deflectometry_items.csv")
    properties_items_path = Path(f"{PAINT_ROOT}/TEMPDATA/properties_items.csv")
    if deflectometry_items_path.exists():
        deflectometry_items = pd.read_csv(deflectometry_items_path)
    else:
        deflectometry_items_path.parent.mkdir(parents=True, exist_ok=True)
        deflectometry_items = pd.DataFrame(
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

    # load heliostat position and reformat for easy parsing
    df_heliostat_positions = load_and_format_heliostat_positions(arguments)

    directory = Path(arguments.input_folder)
    binp_files = directory.rglob("*.binp")

    for input_path in binp_files:
        deflectometry_items, properties_items = extract_data_and_generate_stacs(
            arguments=arguments,
            input_path=input_path,
            df_heliostat_positions=df_heliostat_positions,
            deflectometry_items=deflectometry_items,
            properties_items=properties_items,
        )

    # save deflectometry and facet items for creating collections
    deflectometry_items.to_csv(deflectometry_items_path, index=False)
    properties_items.to_csv(properties_items_path, index=False)


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "generate_deflectometry_and_facet_stacs.py",
        "--input_folder",
        f"{PAINT_ROOT}/ExampleDataKIT",
        "-i_position",
        f"{PAINT_ROOT}/ExampleDataKIT/Heliostatpositionen_xyz.xlsx",
        "--output_path",
        f"{PAINT_ROOT}/ConvertedData",
        "--surface_header_name",
        "=5f2I2f",
        "--facet_header_name",
        "=i9fI",
        "--points_on_facet_struct_name",
        "=7f",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_folder", type=Path, help="Parent folder to search for binary folders."
    )
    parser.add_argument(
        "-i_position",
        "--input_position",
        type=Path,
        help="Path to the heliostat position input file",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    parser.add_argument(
        "--surface_header_name",
        type=str,
        help="The header of the surface struct",
    )
    parser.add_argument(
        "--facet_header_name",
        type=str,
        help="The header of the facet struct",
    )
    parser.add_argument(
        "--points_on_facet_struct_name",
        type=str,
        help="The header of the points on the facet struct",
    )
    args = parser.parse_args()
    main(arguments=args)
