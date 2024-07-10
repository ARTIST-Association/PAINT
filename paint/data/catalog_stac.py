#!/usr/bin/env python

import argparse
import json
import pathlib
from typing import Any, Dict

import paint.util.paint_mappings as mappings


def make_catalog() -> Dict[str, Any]:
    """
    Generate the catalog STAC.

    Returns
    -------
    dict[str, Any]
        The STAC catalog as dictionary
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.CATALOG_ID,
        "type": mappings.CATALOG,
        "title": f"Operational data of concentrating solar power plant {mappings.POWER_PLANT_GPPD_ID}",
        "description": "Calibration images, deflectometry measurements, kinematics and weather data",
        "links": [
            {
                "rel": "self",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "child",
                "href": mappings.CALIBRATION_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the STAC collection containing the calibration data",
            },
        ],
    }


def save_catalog(arguments: argparse.Namespace, catalog: Dict[str, Any]) -> None:
    """
    Save a catalog to disk.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing the output path.
    catalog: dict[str, Any]
        The STAC catalog as dictionary.
    """
    arguments.output.mkdir(parents=True, exist_ok=True)
    with open(arguments.output / mappings.CATALOG_FILE, "w") as handle:
        json.dump(catalog, handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=pathlib.Path, default="stac")
    args = parser.parse_args()

    save_catalog(args, make_catalog())
