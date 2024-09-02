#!/usr/bin/env python

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import (
    calculate_azimuth_and_elevation,
    heliostat_id_to_name,
    to_utc,
)


def find_files_with_ids(folder: Path, id_dict: Dict[Any, Any]) -> None:
    """
    Search for files containing IDs in their names within a given folder or subfolder.

    Parameters
    ----------
    folder : Path
        The root folder to begin the search.
    id_dict : Dict[Any, Any]
        The dictionary to save the IDs of the files that are found.
    """
    for id_ in id_dict:
        # Recursively search for files that contain the ID in their name
        matching_files = list(folder.rglob(f"*{id_}*"))
        id_dict[id_].extend(matching_files)


def main(arguments: argparse.Namespace) -> None:
    """
    Identify which images have not been copied.

    Thie script identifies which images have not been copied from the original location on the LSDF to the correct
    structure.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing input and directory to search for images.
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

    expected_ids = list(data.index.values.astype(str))

    # Dictionaries to store files found for each ID in each location
    files_found_original: Dict[Any, Any] = {id_: [] for id_ in expected_ids}
    files_found_copied: Dict[Any, Any] = {id_: [] for id_ in expected_ids}

    # Find files in both locations
    find_files_with_ids(arguments.original_folder, files_found_original)
    find_files_with_ids(arguments.copied_folder, files_found_copied)

    # List to store IDs and filenames where the ID is only found in one location
    incomplete_ids = []

    for id_ in expected_ids:
        files_in_original = files_found_original[id_]
        files_in_copied = files_found_copied[id_]

        if files_in_original and files_in_copied:
            # ID is present in both locations; mark as complete
            print(f"ID '{id_}' is complete and present in both locations.")
        else:
            # ID is present in only one location
            if files_in_original:
                incomplete_ids.append((id_, str(files_in_original[0])))
            if files_in_copied:
                incomplete_ids.append((id_, str(files_in_copied[0])))

    # Save the incomplete IDs and their respective file paths
    not_copied_path = Path(PAINT_ROOT) / "NOT_COPIED"
    not_copied_path.mkdir(parents=True, exist_ok=True)
    not_copied_full_name = not_copied_path / "not_copied_ids.txt"
    with open(not_copied_full_name, "w") as f:
        for id_, file_path in incomplete_ids:
            f.write(f"{id_}: {file_path}\n")


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    input_folder = Path(lsdf_root) / "paint" / "PAINT" / "CalibrationDataRaw"
    copied_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_calibration = Path(lsdf_root) / "paint" / "PAINT" / "calib_data.csv"

    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "find_missing_images.py",
        "--original_folder",
        str(input_folder),
        "--copied_folder",
        str(copied_folder),
        "--input_calibration",
        str(input_calibration),
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--original_folder",
        type=Path,
        help="Parent folder to search for original images",
    )
    parser.add_argument(
        "--copied_folder", type=Path, help="Parent folder to search for copied images"
    )
    parser.add_argument(
        "--input_calibration",
        type=Path,
    )
    args = parser.parse_args()
    main(arguments=args)
