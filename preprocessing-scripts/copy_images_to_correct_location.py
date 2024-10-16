#!/usr/bin/env python

import argparse
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import (
    calculate_azimuth_and_elevation,
    heliostat_id_to_name,
    to_utc,
)


def find_and_copy_file(
    source_directory: Path, id_str: str, destination_path_and_name: Path
) -> bool:
    """
    Find a given file within a directory or sub directory and copy it to a desired destination.

    Parameters
    ----------
    source_directory : Path
        The source directory to begin the search for the file.
    id_str : str
        The ID string being searched for.
    destination_path_and_name : Path
        The full destination path and file name used for copying the file.

    Returns
    -------
    bool
        Indicating whether an image was copied or not.
    """
    # Walk through all subdirectories of the source directory.
    for root, dirs, files in os.walk(source_directory):
        for file_name in files:
            if file_name == f"{id_str}.png" or file_name.startswith(f"{id_str}_"):
                # Get the full path of the file.
                file_path = os.path.join(root, file_name)

                # Ensure the destination directory exists.
                destination_path_and_name.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file to the destination directory.
                shutil.copy(file_path, destination_path_and_name)

                return True

    return False


def main(arguments: argparse.Namespace) -> None:
    """
    Copy all calibration images into the correct location.

    Parameters
    ----------
    arguments : argparse.Namespace
        The arguments containing input, output path, and directory to search for images.
    """
    # Read in the preprocessing from CSV.
    data = pd.read_csv(arguments.input_calibration, sep=";", decimal=",")
    data.set_index(mappings.ID_INDEX, inplace=True)

    # Convert all timestamps to UTC.
    data[mappings.CREATED_AT] = to_utc(data[mappings.CREATED_AT])
    data[mappings.UPDATED_AT] = to_utc(data[mappings.UPDATED_AT])

    # Compute azimuth and elevation.
    azimuth, elevation = calculate_azimuth_and_elevation(data)
    data[mappings.AZIMUTH] = azimuth
    data[mappings.SUN_ELEVATION] = elevation
    data[mappings.HELIOSTAT_ID] = data[mappings.HELIOSTAT_ID].map(heliostat_id_to_name)

    source = Path(arguments.input_folder)
    failed_copies_list = []
    failed_copies_name = Path(PAINT_ROOT) / "FAILED_COPIES" / "Failed_IDs_2024.csv"
    if failed_copies_name.exists():
        failed_copies_list = pd.read_csv(
            failed_copies_name, index_col=0
        ).index.to_list()
    failed_copies_name.parent.mkdir(parents=True, exist_ok=True)
    # missing_id_path = Path(PAINT_ROOT) / "MISSING_IDS"
    # missing_ids = pd.read_csv(
    #     missing_id_path / "Updated_Missing_IDs.csv", index_col=0
    # ).index.to_list()
    # preprocessing = preprocessing.loc[missing_ids]
    if failed_copies_list:
        data = data.drop(failed_copies_list)
    for heliostat, heliostat_data in data.groupby(mappings.HELIOSTAT_ID):
        for index in heliostat_data.index:
            assert isinstance(heliostat, str)
            id_string = str(index)
            destination_path = (
                Path(arguments.output_path)
                / heliostat
                / mappings.SAVE_CALIBRATION
                / (id_string + ".png")
            )
            copy_success = find_and_copy_file(
                source_directory=source,
                id_str=id_string,
                destination_path_and_name=destination_path,
            )
            if not copy_success:
                print(f"Image ID {id_string} could not be found.")
                failed_copies_list.append(index)
                np.savetxt(failed_copies_name, np.array(failed_copies_list), fmt="%s")

        print(
            f"Group of Heliostat {heliostat} processed -- see above for missed copies!"
        )

    print("All Heliostats have been processed!")


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    input_folder = Path(lsdf_root) / "paint" / "PAINT" / "CalibrationDataRaw" / "2024"
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_calibration = (
        Path(lsdf_root) / "paint" / "PAINT" / "2024_Q1_Q2_calibrationdata.csv"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_folder",
        type=Path,
        help="Parent folder to search for images",
        default=str(input_folder),
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
        default=str(output_folder),
    )
    parser.add_argument(
        "--input_calibration",
        type=Path,
        default=str(input_calibration),
    )
    args = parser.parse_args()
    main(arguments=args)
