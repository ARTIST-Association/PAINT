#!/usr/bin/env python

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.properties_collection_stac import make_properties_collection


def main(arguments: argparse.Namespace) -> None:
    """
    Generate heliostat properties collections.

    This function uses the metadata for each item in the heliostat properties collection to generate a STAC collection.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    df = pd.read_csv(arguments.input_path)

    for heliostat, data in df.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_properties_collection(heliostat_id=heliostat, data=data)
        save_path = (
            Path(arguments.output_path)
            / heliostat
            / mappings.SAVE_PROPERTIES
            / (mappings.HELIOSTAT_PROPERTIES_COLLECTION_FILE % heliostat)
        )
        save_path.parent.mkdir(exist_ok=True, parents=True)
        with open(save_path, "w") as out:
            json.dump(collection, out)


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID

    sys.argv = [
        "generate_properties_collection.py",
        "--input_path",
        f"{PAINT_ROOT}/TEMPDATA/properties_items.csv",
        "--output_path",
        str(output_folder),
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=Path,
        help="Input file containing the heliostat properties items metadata.",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    args = parser.parse_args()
    main(arguments=args)
