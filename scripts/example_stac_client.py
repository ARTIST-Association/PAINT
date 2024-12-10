#!/usr/bin/env python
import argparse

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.stac_client import StacClient
from paint.util import set_logger_config

set_logger_config()

if __name__ == "__main__":
    """
    This is an example script demonstrating different functions of the STAC client.
    """
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to save the downloaded data.",
        default=f"{PAINT_ROOT}/download_test",
    )
    parser.add_argument(
        "--weather_data_sources",
        type=str,
        help="List of data sources to use for weather data.",
        nargs="+",
        choices=["Jülich", "DWD"],
        default=["Jülich", "DWD"],
    )
    parser.add_argument(
        "--start_date",
        type=str,
        help="Start date for filtering the data.",
        default="2023-01-01Z00:00:00Z",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        help="End date for filtering the data.",
        default="2023-03-01Z00:00:00Z",
    )
    parser.add_argument(
        "--heliostats",
        type=str,
        help="List of heliostats to be downloaded.",
        nargs="+",
        default=["AA23", "AA37"],
    )
    parser.add_argument(
        "--collections",
        type=str,
        help="List of collections to be downloaded.",
        nargs="+",
        choices=[
            mappings.SAVE_DEFLECTOMETRY.lower(),
            mappings.SAVE_CALIBRATION.lower(),
            mappings.SAVE_PROPERTIES.lower(),
        ],
        default=["properties", "calibration"],
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

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)

    # Download tower measurements.
    # client.get_tower_measurements()
    #
    # # Download weather data between a certain time period.
    # client.get_weather_data(
    #     data_sources=args.weather_data_sources,
    #     start_date=datetime.strptime(args.start_date, mappings.TIME_FORMAT),
    #     end_date=datetime.strptime(args.end_date, mappings.TIME_FORMAT),
    # )

    # Download heliostat data.
    client.get_heliostat_data(
        heliostats=args.heliostats,
        collections=args.collections,
        filtered_calibration_keys=args.filtered_calibration,
    )

    # Download metadata for all heliostats.
    # WARNING: Running the following line with `heliostats=None` will take a very long time!
    # client.get_heliostat_metadata(heliostats=None)
