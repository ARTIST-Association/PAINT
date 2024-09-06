#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import paint.util.paint_mappings as mappings
from paint.data.catalog_stac import make_catalog
from paint.util.preprocessing import (
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
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    input_axis = Path(lsdf_root) / "paint" / "PAINT" / "axis_data.csv"
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_position = (
        Path(lsdf_root) / "paint" / "PAINT" / "Heliostatpositionen_xyz.xlsx"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_axis", type=Path, default=str(input_axis))
    parser.add_argument(
        "--input_position",
        type=Path,
        default=str(input_position),
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        default=str(output_folder),
    )
    args = parser.parse_args()
    main(args)
