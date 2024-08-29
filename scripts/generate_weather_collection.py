#!/usr/bin/env python

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.weather_collection_stac import make_weather_collection


def main(arguments: argparse.Namespace) -> None:
    """
    Generate a weather collection.

    This function uses the metadata for each item in the weather collection to generate a STAC collection.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    df = pd.read_csv(arguments.input_path)

    collection = make_weather_collection(data=df)
    save_path = Path(arguments.output_path) / mappings.WEATHER_COLLECTION_FILE
    save_path.parent.mkdir(exist_ok=True, parents=True)
    with open(save_path, "w") as out:
        json.dump(collection, out)


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    output_folder = (
        Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID / mappings.SAVE_WEATHER
    )

    sys.argv = [
        "generate_weather_collection.py",
        "--input_path",
        f"{PAINT_ROOT}/TEMPDATA/weather_items.csv",
        "--output_path",
        str(output_folder),
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=Path,
        help="Input file containing the weather items metadata.",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    args = parser.parse_args()
    main(arguments=args)
