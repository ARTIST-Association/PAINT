#!/usr/bin/env python

import argparse
import os
import shutil
import sys
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import (
    calculate_azimuth_and_elevation,
    heliostat_id_to_name,
    to_utc,
)


def find_and_copy_file(
    source_directory: Path, file_name: str, destination_path_and_name: Path
) -> None:
    """
    Find a given file within a directory or sub directory and copy it to a desired destination.

    Parameters
    ----------
    source_directory : Path
        The source directory to begin the search for the file.
    file_name
        The file name being searched for.
    destination_path_and_name
        The full destination path and file name used for copying the file.
    """
    # Walk through all subdirectories of the source directory
    for root, dirs, files in os.walk(source_directory):
        if file_name in files:
            # Get the full path of the file
            file_path = os.path.join(root, file_name)

            # Ensure the destination directory exists
            destination_path_and_name.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file to the destination directory
            shutil.copy(file_path, destination_path_and_name)

            print(
                f"File '{file_name}' found and copied to '{destination_path_and_name}'."
            )
            return

    print(f"File '{file_name}' not found in '{source_directory}'.")


def main(arguments: argparse.Namespace) -> None:
    """
    Copy all calibration images into the correct location.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing input, output path, and directory to search for images.
    """
    # read in the data in CSV
    data = pd.read_csv(arguments.input_calibration)
    data.set_index(mappings.ID_INDEX, inplace=True)

    # convert all timestamps to UTC
    data[mappings.CREATED_AT] = to_utc(data[mappings.CREATED_AT])
    data[mappings.UPDATED_AT] = to_utc(data[mappings.UPDATED_AT])

    # compute azimuth and elevation
    azimuth, elevation = calculate_azimuth_and_elevation(data)
    data[mappings.AZIMUTH] = azimuth
    data[mappings.SUN_ELEVATION] = elevation
    data[mappings.HELIOSTAT_ID] = data[mappings.HELIOSTAT_ID].map(heliostat_id_to_name)

    source = Path(arguments.input_folder)

    for heliostat, heliostat_data in data.groupby(mappings.HELIOSTAT_ID):
        for index in heliostat_data.index:
            assert isinstance(heliostat, str)
            file_name = str(index) + ".png"
            destination_path = (
                Path(arguments.output_path)
                / heliostat
                / mappings.SAVE_CALIBRATION
                / file_name
            )
            find_and_copy_file(
                source_directory=source,
                file_name=file_name,
                destination_path_and_name=destination_path,
            )


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "copy_images_to_correct_location.py",
        "--input_folder",
        f"{PAINT_ROOT}/ExampleDataKIT",
        "--output_path",
        f"{PAINT_ROOT}/ConvertedData",
        "--input_calibration",
        f"{PAINT_ROOT}/ExampleDataKIT/dataframe.csv",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_folder", type=Path, help="Parent folder to search for images"
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    parser.add_argument(
        "--input_calibration",
        type=Path,
        default=f"{PAINT_ROOT}/ExampleDataKIT/dataframe.csv",
    )
    args = parser.parse_args()
    main(arguments=args)
