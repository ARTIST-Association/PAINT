import argparse
import json
import sys
from pathlib import Path

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.catalog_stac import make_catalog
from paint.util.utils import (
    load_and_format_heliostat_axis_data,
    load_and_format_heliostat_positions,
    merge_and_sort_df,
)


def main(arguments: argparse.Namespace) -> None:
    """
    Save a catalog to disk.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing the output path.
    """
    arguments.output_path.mkdir(parents=True, exist_ok=True)
    df_axis = load_and_format_heliostat_axis_data(arguments)
    df_position = load_and_format_heliostat_positions(arguments)
    df = merge_and_sort_df(df_heliostat_positions=df_position, df_axis=df_axis)
    catalog_stac = make_catalog(data=df)
    with open(arguments.output_path / mappings.CATALOG_FILE, "w") as handle:
        json.dump(catalog_stac, handle)


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "generate_catalog.py",
        "--input_axis",
        f"{PAINT_ROOT}/ExampleDataKIT/axis_data.csv",
        "--input_position",
        f"{PAINT_ROOT}/ExampleDataKIT/Heliostatpositionen_xyz.xlsx",
        "--output_path",
        f"{PAINT_ROOT}/ConvertedData",
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_axis", type=Path, default=f"f{PAINT_ROOT}/ExampleDataKIT/axis_data.csv"
    )
    parser.add_argument(
        "--input_position",
        type=Path,
        default=f"{PAINT_ROOT}/ExampleDataKIT/Heliostatpositionen_xyz.xlsx",
    )
    parser.add_argument(
        "--output_path", type=Path, default=f"{PAINT_ROOT}/ConvertedData"
    )
    args = parser.parse_args()
    main(args)
