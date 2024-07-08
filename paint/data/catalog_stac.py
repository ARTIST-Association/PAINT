#!/usr/bin/env python

import argparse
import json
import pathlib

import paint.util.paint_mappings as mappings


def make_catalog(arguments: argparse.Namespace) -> None:
    """
    Generate the catalog STAC.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing the output path.
    """
    catalog = {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.CATALOG_ID,
        "type": mappings.CATALOG,
        "title": f"Operational data of concentrating solar power plant {mappings.POWER_PLANT_GPPD_ID}",
        "description": "Calibration images, deflectometry measurements, kinematics and weather data",
        "links": [
            mappings.LICENSE_LINK,
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

    with open(arguments.output / mappings.CATALOG_FILE, "w") as handle:
        json.dump(catalog, handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=pathlib.Path, default="stac")
    args = parser.parse_args()

    make_catalog(args)
