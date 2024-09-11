#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.calibration_stac import (
    make_calibration_collection,
    make_calibration_item,
)
from paint.util import add_offset_to_lat_lon
from paint.util.utils import (
    calculate_azimuth_and_elevation,
    heliostat_id_to_name,
    to_utc,
)


def main(arguments: argparse.Namespace) -> None:
    """
    Generate STAC items and collections for calibration images.

    Parameters
    ----------
    arguments : argparse.Namespace
        The arguments containing input and output path.
    """
    # Check if saved metadata exists and load if required.
    calibration_items_path = Path(f"{PAINT_ROOT}/TEMPDATA/calibration_items.csv")
    if calibration_items_path.exists():
        calibration_items = pd.read_csv(calibration_items_path)
    else:
        calibration_items_path.parent.mkdir(parents=True, exist_ok=True)
        calibration_items = pd.DataFrame(
            columns=[
                mappings.HELIOSTAT_ID,
                mappings.TITLE_KEY,
                mappings.URL_KEY,
                mappings.CREATED_AT,
                mappings.AZIMUTH,
                mappings.SUN_ELEVATION,
                mappings.SYSTEM,
                mappings.LATITUDE_KEY,
                mappings.LONGITUDE_KEY,
                mappings.ELEVATION,
            ]
        )

    # Read in the data in CSV.
    data = pd.read_csv(arguments.input)
    data.set_index(mappings.ID_INDEX, inplace=True)

    # Convert all timestamps to UTC.
    data[mappings.CREATED_AT] = to_utc(data[mappings.CREATED_AT])
    data[mappings.UPDATED_AT] = to_utc(data[mappings.UPDATED_AT])

    # Compute azimuth and elevation.
    azimuth, elevation = calculate_azimuth_and_elevation(data)
    data[mappings.AZIMUTH] = azimuth
    data[mappings.SUN_ELEVATION] = elevation
    data[mappings.HELIOSTAT_ID] = data[mappings.HELIOSTAT_ID].map(heliostat_id_to_name)

    # Generate the STAC item files for each image.
    for image, heliostat_data in data.iterrows():
        assert isinstance(image, int)
        stac_item = make_calibration_item(image=image, heliostat_data=heliostat_data)
        url = mappings.CALIBRATION_ITEM_URL % (
            heliostat_data[mappings.HELIOSTAT_ID],
            image,
        )
        calibration_items.loc[len(calibration_items)] = [
            heliostat_data[mappings.HELIOSTAT_ID],
            f"calibration image {image} and associated calibration properties for heliostat "
            f"{heliostat_data[mappings.HELIOSTAT_ID]}",
            url,
            heliostat_data[mappings.CREATED_AT],
            heliostat_data[mappings.AZIMUTH],
            heliostat_data[mappings.SUN_ELEVATION],
            heliostat_data[mappings.SYSTEM],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][0],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][1],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][2],
        ]
        calibration_item_stac_path = (
            Path(arguments.output)
            / heliostat_data[mappings.HELIOSTAT_ID]
            / mappings.SAVE_CALIBRATION
            / (mappings.CALIBRATION_ITEM % image)
        )
        calibration_item_stac_path.parent.mkdir(parents=True, exist_ok=True)
        with open(calibration_item_stac_path, "w") as handle:
            json.dump(stac_item, handle)

        # Save associated calibration properties.
        focal_spot_lat, focal_spot_lon = add_offset_to_lat_lon(
            north_offset_m=heliostat_data[mappings.TARGET_OFFSET_N],
            east_offset_m=heliostat_data[mappings.TARGET_OFFSET_E],
        )
        calibration_properties_data = {
            mappings.MOTOR_POS_KEY: {
                mappings.AXIS1_MOTOR: heliostat_data[mappings.AXIS1_MOTOR],
                mappings.AXIS2_MOTOR: heliostat_data[mappings.AXIS2_MOTOR],
            },
            mappings.TARGET_NAME_KEY: mappings.CALIBRATION_TARGET_TO_NAME[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ],
            mappings.FOCAL_SPOT_KEY: {
                mappings.HELIOS_KEY: [
                    focal_spot_lat,
                    focal_spot_lon,
                    heliostat_data[mappings.TARGET_OFFSET_U],
                ],
                mappings.UTIS_KEY: [0, 0, 0],
            },
        }
        save_calibration_properties_path = (
            Path(arguments.output)
            / heliostat_data[mappings.HELIOSTAT_ID]
            / mappings.SAVE_CALIBRATION
            / (mappings.CALIBRATION_PROPERTIES_NAME % image + ".json")
        )
        save_calibration_properties_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_calibration_properties_path, "w") as handle:
            json.dump(calibration_properties_data, handle)

    # Create the STAC collections.
    for heliostat, data in calibration_items.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_calibration_collection(heliostat_id=heliostat, data=data)
        save_path = (
            Path(arguments.output)
            / heliostat
            / mappings.SAVE_CALIBRATION
            / (mappings.CALIBRATION_COLLECTION_FILE % heliostat)
        )
        save_path.parent.mkdir(exist_ok=True, parents=True)
        with open(save_path, "w") as out:
            json.dump(collection, out)


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_calibration = Path(lsdf_root) / "paint" / "PAINT" / "calib_data.csv"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=str(input_calibration),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=str(output_folder),
    )
    args = parser.parse_args()

    main(args)
