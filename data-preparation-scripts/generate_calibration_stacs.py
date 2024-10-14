#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.calibration_stac import (
    make_calibration_collection,
    make_calibration_item,
)
from paint.util import convert_gk_to_lat_long
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
                mappings.LATITUDE_MIN_KEY,
                mappings.LONGITUDE_MIN_KEY,
                mappings.ELEVATION_MIN,
                mappings.LATITUDE_MAX_KEY,
                mappings.LONGITUDE_MAX_KEY,
                mappings.ELEVATION_MAX,
            ]
        )

    # Read in the data in CSV.
    data = pd.read_csv(arguments.input)
    data.set_index(mappings.ID_INDEX, inplace=True)

    # Load list of available images.
    data_available = pd.read_csv(arguments.input_available)

    # Load list of available processed images.
    processed_ids_available = pd.read_csv(
        arguments.input_processed_available, index_col=0
    ).index.values

    # Load UTIS focal spot data.
    utis_data = pd.read_csv(arguments.input_utis)
    utis_data.set_index(mappings.ID_INDEX, inplace=True)

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

    # Identify IDs where processed images are not available.
    no_processed_ids = np.setdiff1d(data.index.values, processed_ids_available)

    num_images = len(data)
    count = 0
    # Generate the STAC item files for each image.
    for image, heliostat_data in data.iterrows():
        assert isinstance(image, int)
        processed_available = True
        if image in no_processed_ids:
            processed_available = False
        stac_item = make_calibration_item(
            image=image,
            heliostat_data=heliostat_data,
            processed_available=processed_available,
        )
        url = mappings.CALIBRATION_ITEM_URL % (
            heliostat_data[mappings.HELIOSTAT_ID],
            image,
        )
        title = (
            f"raw and processed calibration image {image} and associated calibration properties for heliostat "
            f"{heliostat_data[mappings.HELIOSTAT_ID]}"
        )
        if not processed_available:
            title = (
                f"raw calibration image {image} and associated calibration properties for heliostat "
                f"{heliostat_data[mappings.HELIOSTAT_ID]}"
            )
        calibration_items.loc[len(calibration_items)] = [
            heliostat_data[mappings.HELIOSTAT_ID],
            title,
            url,
            heliostat_data[mappings.CREATED_AT],
            heliostat_data[mappings.AZIMUTH],
            heliostat_data[mappings.SUN_ELEVATION],
            heliostat_data[mappings.SYSTEM],
            mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][0],
            mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][1],
            mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][2],
            mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][3],
            mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][4],
            mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][5],
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
        focal_spot_lat, focal_spot_lon = convert_gk_to_lat_long(
            right=mappings.GK_RIGHT_BASE + heliostat_data[mappings.TARGET_OFFSET_E],
            height=mappings.GK_HEIGHT_BASE + heliostat_data[mappings.TARGET_OFFSET_N],
        )
        if processed_available:
            utis_lat, utis_long = convert_gk_to_lat_long(
                right=mappings.GK_RIGHT_BASE + utis_data.loc[image][mappings.UTIS_X],
                height=mappings.GK_HEIGHT_BASE + utis_data.loc[image][mappings.UTIS_Y],
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
                    mappings.UTIS_KEY: [
                        utis_lat,
                        utis_long,
                        utis_data.loc[image][mappings.UTIS_ELEVATION],
                    ],
                },
            }
        else:
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
        count = count + 1
        if count % 1000 == 0:
            print(
                f"I'm alive and have created STACS for {count} of {num_images} - that is {(count/num_images)*100:.2f}%."
            )

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
    print("Script Finished With Success")


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_calibration = Path(lsdf_root) / "paint" / "PAINT" / "calib_data_full.csv"
    input_available = (
        Path(lsdf_root) / "paint" / "PAINT" / "available_calibration_ids.csv"
    )
    input_processed_available = (
        Path(lsdf_root) / "paint" / "PAINT" / "processed_calibration_ids.csv"
    )
    input_utis = Path(lsdf_root) / "paint" / "PAINT" / "utis_focal_points.csv"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=str(input_calibration),
    )
    parser.add_argument(
        "-a",
        "--input_available",
        type=Path,
        default=str(input_available),
    )
    parser.add_argument(
        "-p",
        "--input_processed_available",
        type=Path,
        default=str(input_processed_available),
    )
    parser.add_argument(
        "-u",
        "--input_utis",
        type=Path,
        default=str(input_utis),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=str(output_folder),
    )
    args = parser.parse_args()

    main(args)
