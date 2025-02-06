#!/usr/bin/env python
import argparse
from datetime import datetime

import paint.util.paint_mappings as mappings
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
        default=f"/YOUR/OUTPUT/PATH",
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
        default="2015-01-01Z00:00:00Z",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        help="End date for filtering the data.",
        default="2025-03-01Z00:00:00Z",
    )
    parser.add_argument(
        "--heliostats",
        type=str,
        help="List of heliostats to be downloaded.",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "--collections",
        type=str,
        help="List of collections to be downloaded.",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        default=[ 'flux_image', 'flux_centered_image', 'calibration_properties'],
    )
    args = parser.parse_args()

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)
    # Download metadata for all heliostats.
    # WARNING: Running the following line with `heliostats=None` will take a very long time!
    client.get_heliostat_metadata(heliostats=None)