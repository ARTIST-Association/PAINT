#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import paint.util.paint_mappings as mappings
from paint.data.heliostat_catalog_stac import make_heliostat_catalog


def main(arguments: argparse.Namespace) -> None:
    """
    Generate and save a catalog for each heliostat.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command line arguments.
    """
    if not arguments.output_path.exists():
        arguments.output_path.mkdir(parents=True, exist_ok=True)

    # Iterate through each folder in the main directory.
    for folder in arguments.output_path.iterdir():
        if (
            folder.is_dir() and folder.name != "Weather"
        ):  # Check if it's a directory and not the weather folder.
            # Boolean flags for subfolder existence
            calibration_available = (folder / "Calibration").is_dir()
            deflectometry_available = (folder / "Deflectometry").is_dir()
            properties_available = (folder / "Properties").is_dir()
            helio_catalog = make_heliostat_catalog(
                heliostat_id=folder.name,
                include_deflectometry=deflectometry_available,
                include_calibration=calibration_available,
                include_properties=properties_available,
            )
            save_helio_path = (
                Path(arguments.output_path)
                / folder.name
                / (mappings.HELIOSTAT_CATALOG_FILE % folder.name)
            )
            if not save_helio_path.exists():
                save_helio_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_helio_path, "w") as handle:
                json.dump(helio_catalog, handle)


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
