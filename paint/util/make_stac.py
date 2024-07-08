#!/usr/bin/env python

import argparse
import json
import pathlib

import numpy as np
import pandas as pd

POWER_PLANT_GPPD_ID = "WRI1030197"

COLLECTION_ID = f"{POWER_PLANT_GPPD_ID}-calibration-images"
COLLECTION_FILE = "collection-stac.json"
COLLECTION_URL = f"https://zenodo.org/record/xxx/files/{COLLECTION_FILE}?download=1"

TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"


def make_collection(data: pd.DataFrame) -> dict[str, str]:
    azimuths = np.rad2deg(data["SunPosN"] * 0.5 * np.pi)

    return {
        "stac_version": "1.0.0",
        "stac_extensions": [
            "https://raw.githubusercontent.com/ARTIST-Association/csp/main/json-schema/schema.json",
            "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json",
        ],

        "id": COLLECTION_ID,
        "type": "Collection",

        "title": f"Calibration images of CSP {POWER_PLANT_GPPD_ID}",
        "description": f"All calibration images of the concentrating solar power plant {POWER_PLANT_GPPD_ID} in Jülich, Germany",
        "keywords": [
            "csp",
            "calibration",
            "tracking"
        ],
        "license": "CDLA-2.0",

        "csp:gppd_id": POWER_PLANT_GPPD_ID,

        "providers": [{
            "name": "German Aerospace Center (DLR)",
            "description": "Data producers and power plant operators",
            "roles": [
                "licensor",
                "producer",
                "processor"
            ],
            "url": "https://github.com/ARTIST-Association/PAINT/"
        }, {
            "name": "Karlsruhe Institute of Technology (KIT)",
            "description": "Data processors and software providers",
            "roles": [
                "producer",
                "processor"
            ],
            "url": "https://github.com/ARTIST-Association/PAINT/"
        }],

        "extent": {
            "spatial": {
                "bbox": [[
                    6.387514846666862,
                    50.913296351383806,
                    6.387514846666862,
                    50.913296351383806
                ]]
            },
            "temporal": {
                "interval": [
                    data["CreatedAt"].min().strftime(TIME_FORMAT),
                    data["CreatedAt"].max().strftime(TIME_FORMAT),
                ]
            }
        },

        "summaries": {
            "csp:gppd_id": {
                "type": "string",
                "const": POWER_PLANT_GPPD_ID,
                "count": data.shape[0]
            },
            "datetime": {
                "minimum": data["CreatedAt"].min().strftime(TIME_FORMAT),
                "maximum": data["CreatedAt"].max().strftime(TIME_FORMAT),
            },
            "view:sun_azimuth": {
                "minimum": azimuths.min(),
                "maximum": azimuths.max()
            },
            "view:sun_elevation": {
                "minimum": np.rad2deg(data["SunPosU"]).min(),
                "maximum": np.rad2deg(data["SunPosU"]).max()
            },
            "instruments": list(data["System"].unique())
        },

        "links": [{
            "rel": "license",
            "href": "https://cdla.dev/permissive-2-0/",
            "type": "text/html",
            "title": "Community Data License Agreement – Permissive – Version 2.0"
        }, {
            "rel": "self",
            "href": f"./{COLLECTION_URL}",
            "type": "application/geo+json",
            "title": "Reference to this STAC collection file"
        }, {
            "rel": "root",
            "href": f"./{COLLECTION_URL}",
            "type": "application/geo+json",
            "title": "Reference to this STAC collection file"
        }, {
            "rel": "collection",
            "href": f"./{COLLECTION_URL}",
            "type": "application/geo+json",
            "title": "Reference to this STAC collection file"
        }],

        "assets": {
            "weather": {
                "href": f"./weather.h5",
                "roles": ["data"],
                "type": "application/x-hdf5",
                "title": "Summary of DWD weather data of station Aachen-Orsbach"
            }
        },

        "item_assets": {
            "target": {
                "roles": ["data"],
                "type": "image/png",
                "title": "Calibration image of heliostat"
            }
        }
    }


def make_item(heliostat: int, heliostat_data: pd.Series) -> dict[str, str]:
    return {
        "stac_version": "1.0.0",
        "stac_extensions": [
            "view",
            "https://raw.githubusercontent.com/ARTIST-Association/csp/main/json-schema/schema.json"
        ],

        "id": f"{heliostat}",
        "type": "Feature",

        "title": f"Calibration data of heliostat {heliostat}",
        "description": f"Images of focused sunlight on the calibration target of heliostat {heliostat}",
        "collection": COLLECTION_ID,

        "geometry": {
            "type": "Point",
            "coordinates": [
                6.387514846666862,
                50.913296351383806
            ]
        },

        "properties": {
            "datetime": heliostat_data["CreatedAt"].strftime(TIME_FORMAT),
            "created": heliostat_data["CreatedAt"].strftime(TIME_FORMAT),
            "updated": heliostat_data["UpdatedAt"].strftime(TIME_FORMAT),
            "instruments": [heliostat_data["System"]]
        },

        "view:sun_azimuth": np.rad2deg(heliostat_data["SunPosN"] * 0.5 * np.pi),
        "view:sun_elevation": np.rad2deg(heliostat_data["SunPosU"]),

        "csp:gppd_id": POWER_PLANT_GPPD_ID,
        "csp:target": {
            "csp:target_id": heliostat_data["CalibrationTargetId"],
            "csp:target_offset_e": heliostat_data["TargetOffsetE"],
            "csp:target_offset_n": heliostat_data["TargetOffsetN"],
            "csp:target_offset_u": heliostat_data["TargetOffsetU"],
        },
        "csp:heliostats": [{
            "csp:heliostat_id": heliostat,
            "csp:heliostat_motors": [
                heliostat_data["Axis1MotorPosition"],
                heliostat_data["Axis2MotorPosition"]
            ]
        }],

        "links": [{
            "rel": "self",
            "href": f"./{heliostat}-stac.json",
            "type": "application/geo+json",
            "title": "Reference to this STAC file"
        }, {
            "rel": "root",
            "href": f"{COLLECTION_URL}/{COLLECTION_FILE}",
            "type": "application/geo+json",
            "title": "Reference to the collection STAC file"
        }, {
            "rel": "parent",
            "href": f"{COLLECTION_URL}/{COLLECTION_FILE}",
            "type": "application/geo+json",
            "title": "Reference to the collection STAC file"
        }, {
            "rel": "collection",
            "href": f"{COLLECTION_URL}/{COLLECTION_FILE}",
            "type": "application/geo+json",
            "title": "Reference to the collection STAC file"
        }],

        "assets": {
            "target": {
                "href": f"../{heliostat_data['id']}.png",
                "roles": ["data"],
                "type": "image/png",
                "title": f"Calibration image of heliostat with id {heliostat}"
            }
        }
    }


def to_utc(time_series: pd.Series) -> pd.Series:
    return pd.to_datetime(time_series).dt.tz_localize("Europe/Berlin", ambiguous="infer").dt.tz_convert("UTC")


def convert(arguments: argparse.Namespace) -> None:
    # ensure that the output paths exist
    arguments.output.mkdir(parents=True, exist_ok=True)

    # read in the data in CSV
    data = pd.read_csv(arguments.input)
    data.set_index('HeliostatId', inplace=True)
    
    # convert all timestamps to UTC
    data["CreatedAt"] = to_utc(data["CreatedAt"])
    data["UpdatedAt"] = to_utc(data["UpdatedAt"])

    # generate the STAC item files for each image
    for heliostat, heliostat_data in data.iterrows():
        with open(arguments.output / f"{heliostat}-stac.json", "w") as handle:
            stac_item = make_item(heliostat, heliostat_data)
            json.dump(stac_item, handle)

    # generate the STAC collection
    with open(arguments.output / COLLECTION_FILE, "w") as handle:
        stac_item = make_collection(data)
        json.dump(stac_item, handle)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=pathlib.Path, default="dataframe.csv")
    parser.add_argument("-o", "--output", type=pathlib.Path, default="stac")
    args = parser.parse_args()

    convert(args)
