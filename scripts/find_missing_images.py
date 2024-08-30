#!/usr/bin/env python

import argparse
import os
import sys
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


def main(arguments: argparse.Namespace) -> None:
    """
    Identify which images are not stored on the LSDF, although they should exist according to the metadata file.

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

    missing_ids_path = Path(PAINT_ROOT) / "MISSING_IDS"
    missing_ids_path.mkdir(parents=True, exist_ok=True)

    expected_ids = list(data.index.values.astype(str))

    identified_files = list(arguments.input_folder.rglob("*.png"))
    print_information_count = 0
    for file in identified_files:
        if file.name.split(".")[0] in expected_ids:
            expected_ids.remove(file.name.split(".")[0])
            print_information_count = print_information_count + 1
        elif file.name.split("_")[0] in expected_ids:
            expected_ids.remove(file.name.split("_")[0])
            print_information_count = print_information_count + 1
        if print_information_count % 1000 == 0:
            save_name = (
                missing_ids_path / f"Missing_IDs_after_{print_information_count}.csv"
            )
            np.savetxt(save_name, np.array(expected_ids), fmt="%s")
    final_save_name = missing_ids_path / "Final_Missing_IDs.csv"
    np.savetxt(final_save_name, np.array(expected_ids), fmt="%s")


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    input_folder = Path(lsdf_root) / "paint" / "PAINT" / "CalibrationDataRaw"
    input_calibration = Path(lsdf_root) / "paint" / "PAINT" / "calib_data.csv"

    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "find_missing_images.py",
        "--input_folder",
        str(input_folder),
        "--input_calibration",
        str(input_calibration),
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_folder", type=Path, help="Parent folder to search for images"
    )
    parser.add_argument(
        "--input_calibration",
        type=Path,
    )
    args = parser.parse_args()
    main(arguments=args)
