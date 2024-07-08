#!/usr/bin/env python

import argparse
import json
import pathlib
from typing import Any

import numpy as np
import pandas as pd

import paint.util.paint_mappings as mappings


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
    azimuths = np.rad2deg(data["SunPosN"] * 0.5 * np.pi)

    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [mappings.ITEM_ASSETS_SCHEMA, mappings.CSP_SCHEMA],
        "id": mappings.CALIBRATION_COLLECTION_ID,
        "type": mappings.COLLECTION,
        "title": f"Calibration images of CSP {mappings.POWER_PLANT_GPPD_ID}",
        "description": f"All calibration images of the concentrating solar power plant {mappings.POWER_PLANT_GPPD_ID} in Jülich, Germany",
        "keywords": ["csp", "calibration", "tracking"],
        "license": mappings.CDLA,
        "providers": [mappings.DLR, mappings.KIT],
        "extent": {
            "spatial": {
                "bbox": [
                    [
                        6.387514846666862,
                        50.913296351383806,
                        6.387514846666862,
                        50.913296351383806,
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
            "view:sun_azimuth": {"minimum": azimuths.min(), "maximum": azimuths.max()},
            "view:sun_elevation": {
                "minimum": np.rad2deg(data["SunPosU"]).min(),
                "maximum": np.rad2deg(data["SunPosU"]).max(),
            },
            "instruments": list(data["System"].unique()),
        },
        "links": [
            {
                "rel": "license",
                "href": "https://cdla.dev/permissive-2-0/",
                "type": "text/html",
                "title": "Community Data License Agreement – Permissive – Version 2.0",
            },
            {
                "rel": "self",
                "href": f"./{mappings.CALIBRATION_COLLECTION_URL}",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": f"./{mappings.CALIBRATION_COLLECTION_URL}",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "collection",
                "href": f"./{mappings.CALIBRATION_COLLECTION_URL}",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
        ],
        "item_assets": {
            "target": {
                "roles": ["data"],
                "type": "image/png",
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
        "title": f"Calibration data of heliostat {image}",
        "description": f"Images of focused sunlight on the calibration target of heliostat {image}",
        "collection": mappings.CALIBRATION_COLLECTION_ID,
        "geometry": {
            "type": "Point",
            "coordinates": [6.387514846666862, 50.913296351383806],
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
            "instruments": [heliostat_data["System"]],
        },
        "view:sun_azimuth": np.rad2deg(heliostat_data["SunPosN"] * 0.5 * np.pi),
        "view:sun_elevation": np.rad2deg(heliostat_data["SunPosU"]),
        "csp:gppd_id": mappings.POWER_PLANT_GPPD_ID,
        "csp:target": {
            "csp:target_id": heliostat_data["CalibrationTargetId"],
            "csp:target_offset_e": heliostat_data["TargetOffsetE"],
            "csp:target_offset_n": heliostat_data["TargetOffsetN"],
            "csp:target_offset_u": heliostat_data["TargetOffsetU"],
        },
        "csp:heliostats": [
            {
                "csp:heliostat_id": image,
                "csp:heliostat_motors": [
                    heliostat_data["Axis1MotorPosition"],
                    heliostat_data["Axis2MotorPosition"],
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
                "href": f"{mappings.CALIBRATION_COLLECTION_URL}/{mappings.CALIBRATION_COLLECTION_FILE}",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
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
                "type": "image/png",
                "title": f"Calibration image of heliostat with id {image}",
            }
        },
    }


def to_utc(time_series: pd.Series) -> pd.Series:
    """
    Parse local datetime strings and convert to UTC.

    Parameters
    ----------
    time_series : pd.Series
        The series containing the local datetime strings.

    Returns
    -------
    pd.Series
        The corresponding UTC datetime objects.
    """
    return (
        pd.to_datetime(time_series)
        .dt.tz_localize("Europe/Berlin", ambiguous="infer")
        .dt.tz_convert("UTC")
    )


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
    data.set_index(mappings.HELIOSTAT_ID, inplace=True)

    # convert all timestamps to UTC
    data[mappings.CREATED_AT] = to_utc(data[mappings.CREATED_AT])
    data[mappings.UPDATED_AT] = to_utc(data[mappings.UPDATED_AT])

    # generate the STAC item files for each image
    for heliostat, heliostat_data in data.iterrows():
        with open(arguments.output / f"{heliostat}-stac.json", "w") as handle:
            stac_item = make_item(heliostat, heliostat_data)
            json.dump(stac_item, handle)

    # generate the STAC collection
    with open(arguments.output / mappings.CALIBRATION_COLLECTION_FILE, "w") as handle:
        stac_item = make_collection(data)
        json.dump(stac_item, handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=pathlib.Path, default="dataframe.csv")
    parser.add_argument("-o", "--output", type=pathlib.Path, default="stac")
    args = parser.parse_args()

    convert(args)
