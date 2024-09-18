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
    Copy all processed calibration images into the correct location.

    Parameters
    ----------
    arguments : argparse.Namespace
        The arguments containing input, output path, and directory to search for images.
    """
    # Read in the data from CSV.
    data = pd.read_csv(arguments.input_calibration)
    data.set_index(mappings.ID_INDEX, inplace=True)

    # Load list of available images.
    data_available = pd.read_csv(arguments.input_available)

    # Load list of available processed images
    processed_ids_available = pd.read_csv(
        arguments.input_processed_available, index_col=0
    ).index.values

    # Convert all timestamps to UTC.
    data[mappings.CREATED_AT] = to_utc(data[mappings.CREATED_AT])
    data[mappings.UPDATED_AT] = to_utc(data[mappings.UPDATED_AT])

    # Compute azimuth and elevation.
    azimuth, elevation = calculate_azimuth_and_elevation(data)
    data[mappings.AZIMUTH] = azimuth
    data[mappings.SUN_ELEVATION] = elevation
    data[mappings.HELIOSTAT_ID] = data[mappings.HELIOSTAT_ID].map(heliostat_id_to_name)

    # Filter data to only include metadata for the images on the LSDF.
    data = data.loc[data_available["ID"].values]

    # Remove duplicated IDs (the last occurrence has updated measurements removing some NaN values).
    data = data[~data.index.duplicated(keep="last")]

    # Only consider IDs for which processed data is available
    data = data.loc[processed_ids_available]

    failed_copy_list = []
    failed_copy_name = (
        Path(PAINT_ROOT) / f"{arguments.name_key} failed copies" / "failed_copy.csv"
    )
    if failed_copy_name.exists():
        failed_copy_list = pd.read_csv(failed_copy_name, index_col=0).index.to_list()
    failed_copy_name.parent.mkdir(parents=True, exist_ok=True)
    source = Path(arguments.input_folder)

    # Check which files have already been copied.
    already_copied_files = list(
        arguments.output_folder.rglob(f"*_{arguments.name_key}.png")
    )
    already_copied_list = [
        file.stem.split("_")[0].asint() for file in already_copied_files
    ]

    # Drop files that have already been copied.
    if already_copied_list:
        data = data.drop(already_copied_list)
    for heliostat, heliostat_data in data.groupby(mappings.HELIOSTAT_ID):
        for index in heliostat_data.index:
            assert isinstance(heliostat, str)
            id_string = str(index)
            destination_path = (
                Path(arguments.output_path)
                / heliostat
                / mappings.SAVE_CALIBRATION
                / (id_string + "_" + arguments.name_key + ".png")
            )
            copy_success = find_and_copy_file(
                source_directory=source,
                id_str=id_string,
                destination_path_and_name=destination_path,
            )
            if not copy_success:
                print(f"Image ID {id_string} could not be found.")
                failed_copy_list.append(index)
                np.savetxt(failed_copy_name, np.array(failed_copy_list), fmt="%s")

        print(
            f"Group of Heliostat {heliostat} processed -- see above for missed copies!"
        )

    print("All Heliostats have been processed!")


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    input_folder = Path(lsdf_root) / "paint" / "PAINT" / "CalibrationDataCropped"
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_calibration = Path(lsdf_root) / "paint" / "PAINT" / "calib_data_full.csv"
    input_available = (
        Path(lsdf_root) / "paint" / "PAINT" / "available_calibration_ids.csv"
    )
    input_processed_available = (
        Path(lsdf_root) / "paint" / "PAINT" / "processed_calibration_ids.csv"
    )
    name_key = "cropped"

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
    parser.add_argument(
        "--input_available",
        type=Path,
        default=str(input_available),
    )
    parser.add_argument(
        "--input_processed_available",
        type=Path,
        default=str(input_processed_available),
    )
    parser.add_argument(
        "--name_key",
        type=str,
        default=name_key,
    )
    args = parser.parse_args()
    main(arguments=args)
