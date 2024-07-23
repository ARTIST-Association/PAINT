import argparse
import json
import sys
from pathlib import Path

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.heliostat_catalog_stac import make_heliostat_catalog
from paint.util.utils import (
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
    for heliostat, _ in df.iterrows():
        assert isinstance(heliostat, str)
        helio_catalog = make_heliostat_catalog(heliostat_id=heliostat)
        save_helio_path = (
            Path(arguments.output_path)
            / heliostat
            / (mappings.HELIOSTAT_CATALOG_FILE % heliostat)
        )
        save_helio_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_helio_path, "w") as handle:
            json.dump(helio_catalog, handle)


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "generate_heliostat_catalog.py",
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
