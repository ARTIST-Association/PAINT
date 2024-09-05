#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import paint.util.paint_mappings as mappings
from paint.data.tower_measurements import get_tower_measurements
from paint.data.tower_stac import make_tower_item


def main(arguments: argparse.Namespace) -> None:
    """
    Load the tower measurements, save these as a Json, and generate the associated STAC item.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing the output path.
    """
    # Load measurements
    extreme_measurements, tower_measurements = get_tower_measurements()

    # Create STAC item
    tower_stac = make_tower_item(extreme_measurements)

    # Create file paths exist
    tower_measurements_path = Path(arguments.output) / (
        mappings.TOWER_FILE_NAME + ".json"
    )
    tower_item_stac_path = Path(arguments.output) / (mappings.TOWER_STAC_NAME + ".json")

    # Check the file path exists
    tower_measurements_path.parent.mkdir(parents=True, exist_ok=True)
    tower_item_stac_path.parent.mkdir(parents=True, exist_ok=True)

    # Save measurements
    with open(tower_measurements_path, "w") as handle:
        json.dump(tower_measurements, handle)

    # Save STAC item
    with open(tower_item_stac_path, "w") as handle:
        json.dump(tower_stac, handle)


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    output_folder = Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=str(output_folder),
    )
    args = parser.parse_args()

    main(args)
