#!/usr/bin/env python

import argparse
import json
import os
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
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    output_folder = (
        Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID / mappings.SAVE_WEATHER
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=Path,
        help="Input file containing the weather items metadata.",
        default=f"{PAINT_ROOT}/TEMPDATA/weather_items.csv",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
        default=str(output_folder),
    )
    args = parser.parse_args()
    main(arguments=args)
