#!/usr/bin/env python
import argparse
from datetime import datetime

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.stac_client import StacClient

if __name__ == "__main__":
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
        default=["properties", "calibration"],
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        default=["cropped_image", "calibration_properties"],
    )
    args = parser.parse_args()

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)
    client.get_tower_measurements()
    client.get_weather_data(
        data_sources=args.weather_data_sources,
        start_date=datetime.strptime(args.start_date, mappings.TIME_FORMAT),
        end_date=datetime.strptime(args.end_date, mappings.TIME_FORMAT),
    )
    client.get_heliostat_data(
        heliostats=args.heliostats,
        collections=args.collections,
        filtered_calibration_keys=args.filtered_calibration,
    )