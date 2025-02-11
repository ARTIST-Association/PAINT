#!/usr/bin/env python
import argparse

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
        default="/YOUR/OUTPUT/PATH",
    )
    args = parser.parse_args()

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)
    # Download metadata for all heliostats.
    # WARNING: Running the following line will take a very long time!
    client.get_heliostat_metadata(heliostats=None)
