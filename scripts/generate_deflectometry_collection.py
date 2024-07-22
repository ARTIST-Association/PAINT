#!/usr/bin/env python

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.deflectometry_stac import make_deflectometry_collection


def main(arguments: argparse.Namespace) -> None:
    """
    Generate deflectometry collections.

    This function uses the metadata for each item in the deflectometry collection to generate a STAC collection.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    df = pd.read_csv(arguments.input_path)

    for heliostat, data in df.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_deflectometry_collection(heliostat_id=heliostat, data=data)
        save_path = (
            Path(arguments.output_path)
            / heliostat
            / mappings.SAVE_DEFLECTOMETRY
            / (mappings.DEFLECTOMETRY_COLLECTION_FILE % heliostat)
        )
        save_path.parent.mkdir(exist_ok=True, parents=True)
        with open(save_path, "w") as out:
            json.dump(collection, out)


if __name__ == "__main__":
    sys.argv = [
        "generate_deflectometry_collection.py",
        "--input_path",
        f"{PAINT_ROOT}/TEMPDATA/deflectometry_items.csv",
        "--output_path",
        f"{PAINT_ROOT}/ConvertedData",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=Path,
        help="Input file containing the deflectometry items metadata.",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    args = parser.parse_args()
    main(arguments=args)
