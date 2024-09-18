#!/usr/bin/env python

import argparse
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.binary_extractor import BinaryExtractor
from paint.data.deflectometry_stac import (
    make_deflectometry_collection,
    make_deflectometry_item,
)
from paint.util.preprocessing import load_and_format_heliostat_positions


def extract_data_and_generate_stacs(
    arguments: argparse.Namespace,
    input_path: Path,
    df_heliostat_positions: pd.DataFrame,
    deflectometry_items: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract the binary data and generate STACS.

    This function extracts the binary data from the ``.binp`` file. After this data is extracted, it also generates
    the STAC items for the deflectometry measurement. Additionally, it collects the summary PDFs for the deflectometry
    measurement, renames them, copies them to the appropriate location and generates a STAC for this PDF.

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

    Returns
    -------
    pd.DataFrame:
        A dataframe containing the metadata for all items in the deflectometry collection.
    """
    # Extract binary data
    converter = BinaryExtractor(
        input_path=input_path,
        output_path=arguments.output_path,
        surface_header_name=arguments.surface_header_name,
        facet_header_name=arguments.facet_header_name,
        points_on_facet_struct_name=arguments.points_on_facet_struct_name,
    )
    converter.convert_to_h5()
    metadata = df_heliostat_positions.loc[converter.heliostat_id][
        [
            mappings.EAST_KEY,
            mappings.NORTH_KEY,
            mappings.ALTITUDE_KEY,
            mappings.HEIGHT_ABOVE_GROUND,
        ]
    ]
    metadata[mappings.CREATED_AT] = converter.deflectometry_created_at

    # STAC contains all deflectometry items, therefore, only create the stac once after the raw conversion
    if converter.raw_data:
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

        # create stac and extract latitude and longitude
        lat_lon, stac_item = make_deflectometry_item(
            heliostat_key=converter.heliostat_id,
            heliostat_data=metadata,
        )
        # Save item metadata for collection creation later.
        url = mappings.DEFLECTOMETRY_ITEM_URL % (
            converter.heliostat_id,
            converter.heliostat_id,
            converter.deflectometry_created_at,
        )
        deflectometry_items.loc[len(deflectometry_items)] = [
            converter.heliostat_id,
            f"Deflectometry measurements for {converter.heliostat_id} at {converter.deflectometry_created_at}",
            url,
            converter.deflectometry_created_at,
            lat_lon[0],
            lat_lon[1],
            metadata[mappings.ALTITUDE_KEY],
        ]

        # save the deflectometry measurement stac
        save_deflectometry_path = (
            Path(arguments.output_path)
            / converter.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / (
                mappings.DEFLECTOMETRY_ITEM
                % (converter.heliostat_id, converter.deflectometry_created_at)
            )
        )
        save_deflectometry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_deflectometry_path, mode="w") as handle:
            json.dump(stac_item, handle)

    return deflectometry_items


def main(arguments: argparse.Namespace):
    """
    Generate deflectometry STACS and facet item STACS.

    This function converts binary data to HDF5 for deflectometry measurements.
    Additionally, the deflectometry results summary PDF is moved to the correct location and renamed. Also, the STAC
    items and collections for deflectometry measurements are created.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    # check if saved metadata exists and load if required
    deflectometry_items_path = Path(f"{PAINT_ROOT}/TEMPDATA/deflectometry_items.csv")
    if deflectometry_items_path.exists():
        deflectometry_items = pd.read_csv(deflectometry_items_path, index_col=0)
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

    # load heliostat position and reformat for easy parsing
    df_heliostat_positions = load_and_format_heliostat_positions(arguments)

    directory = Path(arguments.input_folder)
    binp_files = directory.rglob("*.binp")

    already_copied_files_path = (
        Path(PAINT_ROOT) / "Deflectometry" / "already_copied.csv"
    )
    if already_copied_files_path.exists():
        already_copied_list = pd.read_csv(
            already_copied_files_path, index_col=0
        ).index.to_list()
    else:
        already_copied_files_path.parent.mkdir(parents=True, exist_ok=True)
        already_copied_list = []
    for input_path in binp_files:
        if str(input_path) in already_copied_list:
            print("SKipping {input_path} since already copied")
        else:
            deflectometry_items = extract_data_and_generate_stacs(
                arguments=arguments,
                input_path=input_path,
                df_heliostat_positions=df_heliostat_positions,
                deflectometry_items=deflectometry_items,
            )
            deflectometry_items.to_csv(deflectometry_items_path)
            already_copied_list.append(input_path)
            np.savetxt(
                already_copied_files_path, np.array(already_copied_list), fmt="%s"
            )
            print(f"Finished copying {input_path}")

    for heliostat, data in deflectometry_items.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_deflectometry_collection(heliostat_id=heliostat, data=data)
        save_path = (
            Path(arguments.output_path)
            / heliostat
            / mappings.SAVE_DEFLECTOMETRY
            / (mappings.DEFLECTOMETRY_COLLECTION_FILE % heliostat)
        )
        save_path.parent.mkdir(exist_ok=True, parents=True)
        with open(save_path, "w") as out:
            json.dump(collection, out)


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    input_folder = Path(lsdf_root) / "paint" / "DeflecDaten"
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_position = (
        Path(lsdf_root) / "paint" / "PAINT" / "Heliostatpositionen_xyz.xlsx"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_folder",
        type=Path,
        help="Parent folder to search for binary folders.",
        default=str(input_folder),
    )
    parser.add_argument(
        "--input_position",
        type=Path,
        help="Path to the heliostat position input file",
        default=str(input_position),
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
        default=str(output_folder),
    )
    parser.add_argument(
        "--surface_header_name",
        type=str,
        help="The header of the surface struct",
        default="=5f2I2f",
    )
    parser.add_argument(
        "--facet_header_name",
        type=str,
        help="The header of the facet struct",
        default="=i9fI",
    )
    parser.add_argument(
        "--points_on_facet_struct_name",
        type=str,
        help="The header of the points on the facet struct",
        default="=7f",
    )
    args = parser.parse_args()
    main(arguments=args)
