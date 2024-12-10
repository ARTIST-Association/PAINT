#!/usr/bin/env python
import argparse
import pathlib

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.stac_client import StacClient
from paint.util import set_logger_config

set_logger_config()

if __name__ == "__main__":
    """
    This is an example script demonstrating how the STAC client can be used to access single calibration items via
    the calibration item ID.
    """
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=pathlib.Path,
        help="Path to save the downloaded data.",
        default=f"{PAINT_ROOT}/download_calibration_test",
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        choices=[
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
            mappings.CALIBRATION_PROPERTIES_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
        ],
        default=["cropped_image", "calibration_properties"],
    )
    args = parser.parse_args()

    # Parameters for demonstration purposes:
    single_heliostat = "AA23"
    single_id = 123819

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)

    # Download single item.
    client.get_single_calibration_item_by_id(
        heliostat_id=single_heliostat,
        item_id=single_id,
        filtered_calibration_keys=args.filtered_calibration,
    )

    # Parameters for downloading multiple calibration items or all items for heliostats:
    heliostat_items_dict = {"AA27": [100750, 101103, 102950], "AA39": None}
    client.get_multiple_calibration_items_by_id(
        heliostat_items_dict=heliostat_items_dict,
        filtered_calibration_keys=args.filtered_calibration,
    )
