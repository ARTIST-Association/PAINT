#!/usr/bin/env python
import argparse

from paint import PAINT_ROOT
from paint.data.stac_client import StacClient
from paint.util import set_logger_config

set_logger_config()

if __name__ == "__main__":
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to save the downloaded data.",
        default=f"{PAINT_ROOT}/download_calibration_test",
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        default=["cropped_image", "calibration_properties"],
    )
    args = parser.parse_args()

    # Parameters for demonstration purposes.
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

    # Parameters for downloading multiple calibration items or all items for heliostats.
    heliostat_items_dict = {"AA27": [100750, 101103, 102950], "AA39": None}
    client.get_multiple_calibration_items_by_id(
        heliostat_items_dict=heliostat_items_dict,
        filtered_calibration_keys=args.filtered_calibration,
    )
