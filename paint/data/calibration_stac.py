#!/usr/bin/env python

import argparse
import json
import pathlib
from typing import Any

import pandas as pd

import paint.util.paint_mappings as mappings
import paint.util.utils as utils


def make_collection(data: pd.DataFrame) -> dict[str, Any]:
    """
    Generate the STAC collection.

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe containing all image data.

    Returns
    -------
    dict[str, Any]
        The STAC collection as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [mappings.ITEM_ASSETS_SCHEMA, mappings.CSP_SCHEMA],
        "id": mappings.CALIBRATION_COLLECTION_ID,
        "type": mappings.COLLECTION,
        "title": f"Calibration images of CSP {mappings.POWER_PLANT_GPPD_ID}",
        "description": f"All calibration images of the concentrating solar power plant {mappings.POWER_PLANT_GPPD_ID} in Jülich, Germany",
        "keywords": ["csp", "calibration", "tracking"],
        "license": mappings.LICENSE,
        "providers": [mappings.DLR, mappings.KIT],
        "extent": {
            "spatial": {
                "bbox": [
                    [
                        mappings.POWER_PLANT_LON,
                        mappings.POWER_PLANT_LAT,
                        mappings.POWER_PLANT_LON,
                        mappings.POWER_PLANT_LAT,
                    ]
                ]
            },
            "temporal": {
                "interval": [
                    data[mappings.CREATED_AT].min().strftime(mappings.TIME_FORMAT),
                    data[mappings.CREATED_AT].max().strftime(mappings.TIME_FORMAT),
                ]
            },
        },
        "summaries": {
            "csp:gppd_id": {
                "type": "string",
                "const": mappings.POWER_PLANT_GPPD_ID,
                "count": data.shape[0],
            },
            "datetime": {
                "minimum": data[mappings.CREATED_AT]
                .min()
                .strftime(mappings.TIME_FORMAT),
                "maximum": data[mappings.CREATED_AT]
                .max()
                .strftime(mappings.TIME_FORMAT),
            },
            "view:sun_azimuth": {
                "minimum": data[mappings.AZIMUTH].min(),
                "maximum": data[mappings.AZIMUTH].max(),
            },
            "view:sun_elevation": {
                "minimum": data[mappings.ELEVATION].min(),
                "maximum": data[mappings.ELEVATION].max(),
            },
            "instruments": list(data[mappings.SYSTEM].unique()),
        },
        "links": [
            mappings.LICENSE_LINK,
            {
                "rel": "self",
                "href": mappings.CALIBRATION_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the entire catalogue for {mappings.POWER_PLANT_GPPD_ID}",
            },
            {
                "rel": "collection",
                "href": mappings.CALIBRATION_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
        ]
        + [
            {
                "rel": "item",
                "href": mappings.CALIBRATION_ITEM_URL % image,
                "type": mappings.MIME_GEOJSON,
                "title": f"STAC item of image {image}",
            }
            for image, _ in data.iterrows()
        ],
        "item_assets": {
            "target": {
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": "Calibration images of heliostats",
            }
        },
    }


def make_item(image: int, heliostat_data: pd.Series) -> dict[str, Any]:
    """
    Generate a STAC item for an image.

    Parameters
    ----------
    image: int
        The image id.
    heliostat_data: pd.Series.
        The data belonging to the heliostat.

    Returns
    -------
    dict[str, Any]
        The STAC item data as dictionary.
    """
    return {
        "stac_version": "1.0.0",
        "stac_extensions": [
            "view",
            "https://raw.githubusercontent.com/ARTIST-Association/csp/main/json-schema/schema.json",
        ],
        "id": f"{image}",
        "type": "Feature",
        "title": f"Calibration of heliostat {image}",
        "description": f"Images of focused sunlight on the calibration target of heliostat {image}",
        "collection": mappings.CALIBRATION_COLLECTION_ID,
        "geometry": {
            "type": "Point",
            "coordinates": [mappings.POWER_PLANT_LON, mappings.POWER_PLANT_LAT],
        },
        "properties": {
            "datetime": heliostat_data[mappings.CREATED_AT].strftime(
                mappings.TIME_FORMAT
            ),
            "created": heliostat_data[mappings.CREATED_AT].strftime(
                mappings.TIME_FORMAT
            ),
            "updated": heliostat_data[mappings.UPDATED_AT].strftime(
                mappings.TIME_FORMAT
            ),
            "instruments": [heliostat_data[mappings.SYSTEM]],
        },
        "view:sun_azimuth": heliostat_data[mappings.AZIMUTH],
        "view:sun_elevation": heliostat_data[mappings.ELEVATION],
        "csp:gppd_id": mappings.POWER_PLANT_GPPD_ID,
        "csp:target_id": heliostat_data[mappings.CALIBRATION_TARGET],
        "csp:heliostats": [
            {
                "csp:heliostat_id": heliostat_data[mappings.HELIOSTAT_ID],
                "csp:heliostat_motors": [
                    heliostat_data[mappings.AXIS1_MOTOR],
                    heliostat_data[mappings.AXIS2_MOTOR],
                ],
            }
        ],
        "links": [
            {
                "rel": "self",
                "href": f"./{image}-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": f"./{mappings.CATALOGUE_URL}",
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the entire catalogue for {mappings.POWER_PLANT_GPPD_ID}",
            },
            {
                "rel": "parent",
                "href": f"{mappings.CALIBRATION_COLLECTION_URL}/{mappings.CALIBRATION_COLLECTION_FILE}",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": f"{mappings.CALIBRATION_COLLECTION_URL}/{mappings.CALIBRATION_COLLECTION_FILE}",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "target": {
                "href": f"../{image}.png",
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": f"Calibration image of heliostat with id {image}",
            }
        },
    }


def convert(arguments: argparse.Namespace) -> None:
    """
    Convert an internal CSV file to STAC.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing input and output path.
    """
    # ensure that the output paths exist
    arguments.output.mkdir(parents=True, exist_ok=True)

    # read in the data in CSV
    data = pd.read_csv(arguments.input)
    data.set_index(mappings.ID_INDEX, inplace=True)

    # convert all timestamps to UTC
    data[mappings.CREATED_AT] = utils.to_utc(data[mappings.CREATED_AT])
    data[mappings.UPDATED_AT] = utils.to_utc(data[mappings.UPDATED_AT])

    # compute azimuth and elevation
    azimuth, elevation = utils.calculate_azimuth_and_elevation(data)
    data[mappings.AZIMUTH] = azimuth
    data[mappings.ELEVATION] = elevation

    # generate the STAC item files for each image
    for image, heliostat_data in data.iterrows():
        with open(
            arguments.output / (mappings.CALIBRATION_ITEM % image), "w"
        ) as handle:
            stac_item = make_item(image, heliostat_data)
            json.dump(stac_item, handle)

    # generate the STAC collection
    with open(arguments.output / mappings.CALIBRATION_COLLECTION_FILE, "w") as handle:
        stac_item = make_collection(data)
        json.dump(stac_item, handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        default="/Users/mgoetz/Downloads/ExampleDataKIT/dataframe.csv",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default="/Users/mgoetz/Downloads/ExampleDataKIT/stac",
    )
    args = parser.parse_args()

    convert(args)
