#!/usr/bin/env python

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint.data.heliostat_catalog_stac import make_heliostat_catalog
from paint.util.preprocessing import (
    load_and_format_heliostat_axis_data,
    load_and_format_heliostat_positions,
    merge_and_sort_df,
)


def main(arguments: argparse.Namespace) -> None:
    """
    Generate and save a catalog for each heliostat.

    Parameters
    ----------
    arguments: argparse.Namespace
        The command line arguments.
    """
    arguments.output_path.mkdir(parents=True, exist_ok=True)
    df_axis = load_and_format_heliostat_axis_data(arguments)
    df_position = load_and_format_heliostat_positions(arguments)
    df = merge_and_sort_df(df_heliostat_positions=df_position, df_axis=df_axis)
    heliostats_with_deflectometry = pd.read_excel(
        arguments.input_deflectometry_available
    ).dropna()[mappings.INTERNAL_NAME_INDEX]
    for heliostat, _ in df.iterrows():
        assert isinstance(heliostat, str)
        if heliostat in heliostats_with_deflectometry.values:
            helio_catalog = make_heliostat_catalog(
                heliostat_id=heliostat, include_deflectometry=True
            )
        else:
            helio_catalog = make_heliostat_catalog(
                heliostat_id=heliostat, include_deflectometry=False
            )
        save_helio_path = (
            Path(arguments.output_path)
            / heliostat
            / (mappings.HELIOSTAT_CATALOG_FILE % heliostat)
        )
        save_helio_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_helio_path, "w") as handle:
            json.dump(helio_catalog, handle)


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    input_axis = Path(lsdf_root) / "paint" / "PAINT" / "axis_data.csv"
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    input_position = (
        Path(lsdf_root) / "paint" / "PAINT" / "Heliostatpositionen_xyz.xlsx"
    )
    input_deflectometry_available = (
        Path(lsdf_root) / "paint" / "PAINT" / "deflec_availability.xlsx"
    )

    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "generate_heliostat_catalog.py",
        "--input_axis",
        str(input_axis),
        "--input_position",
        str(input_position),
        "--input_deflectometry_available",
        str(input_deflectometry_available),
        "--output_path",
        str(output_folder),
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_axis",
        type=Path,
    )
    parser.add_argument(
        "--input_position",
        type=Path,
    )
    parser.add_argument(
        "--input_deflectometry_available",
        type=Path,
    )
    parser.add_argument(
        "--output_path",
        type=Path,
    )
    args = parser.parse_args()
    main(args)
