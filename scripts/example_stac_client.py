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
        "--include_juelich",
        type=bool,
        help="Boolean indicating whether to include Jülich weather data.",
        default=True,
    )
    parser.add_argument(
        "--include_dwd",
        type=bool,
        help="Boolean indicating whether to include DWD weather data.",
        default=False,
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
        default=["AA23"],
    )
    parser.add_argument(
        "--include_calibration",
        type=bool,
        help="Boolean indicating whether to include calibration data.",
        default=False,
    )
    parser.add_argument(
        "--include_deflectometry",
        type=bool,
        help="Boolean indicating whether to include deflectometry data.",
        default=True,
    )
    parser.add_argument(
        "--include_properties",
        type=bool,
        help="Boolean indicating whether to include heliostat properties data.",
        default=True,
    )
    args = parser.parse_args()

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)
    client.get_tower_measurements()
    client.get_weather_data(
        include_dwd=args.include_dwd,
        include_juelich=args.include_juelich,
        start_date=datetime.strptime(args.start_date, mappings.TIME_FORMAT),
        end_date=datetime.strptime(args.end_date, mappings.TIME_FORMAT),
    )
    client.get_heliostat_data(
        heliostats=args.heliostats,
        get_calibration=args.include_calibration,
        get_deflectometry=args.include_deflectometry,
        get_properties=args.include_properties,
    )
