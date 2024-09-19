#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import paint.util.paint_mappings as mappings
from paint.data.catalog_stac import make_catalog


def main(arguments: argparse.Namespace) -> None:
    """
    Save a catalog to disk.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing the output path.
    """
    if not arguments.output_path.exists():
        arguments.output_path.mkdir(parents=True, exist_ok=True)

    list_of_heliostats = []

    # Iterate through each folder in the main directory
    for folder in arguments.output_path.iterdir():
        if folder.is_dir():
            if folder.name != "Weather":
                list_of_heliostats.append(folder.name)

    catalog_stac = make_catalog(data=list_of_heliostats)
    with open(arguments.output_path / mappings.CATALOG_FILE, "w") as handle:
        json.dump(catalog_stac, handle)


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_path",
        type=Path,
        default=str(output_folder),
    )
    args = parser.parse_args()
    main(args)
