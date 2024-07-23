#!/usr/bin/env python

from typing import Any, Dict

import pandas as pd

import paint.util.paint_mappings as mappings


def make_calibration_collection(
    heliostat_id: str, data: pd.DataFrame
) -> Dict[str, Any]:
    """
    Generate the STAC collection.

    Parameters
    ----------
    heliostat_id: str
        The heliostat id of the heliostat being considered.
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
        "id": mappings.CALIBRATION_COLLECTION_ID % heliostat_id,
        "type": mappings.COLLECTION,
        "title": f"Calibration images from heliostat {heliostat_id}",
        "description": f"All calibration images from the heliostat {heliostat_id}",
        "keywords": ["csp", "calibration", "tracking"],
        "license": mappings.LICENSE,
        "providers": [mappings.DLR, mappings.KIT],
        "extent": {
            "spatial": {
                "bbox": [
                    mappings.POWER_PLANT_LAT,
                    mappings.POWER_PLANT_LON,
                    mappings.POWER_PLANT_LAT,
                    mappings.POWER_PLANT_LON,
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
                "minimum": data[mappings.SUN_ELEVATION].min(),
                "maximum": data[mappings.SUN_ELEVATION].max(),
            },
            "instruments": list(data[mappings.SYSTEM].unique()),
        },
        "links": [
            mappings.LICENSE_LINK,
            {
                "rel": "self",
                "href": mappings.CALIBRATION_COLLECTION_URL % heliostat_id,
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
                "href": mappings.CALIBRATION_COLLECTION_URL % heliostat_id,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
        ]
        + [
            {
                "rel": "item",
                "href": data_row[mappings.URL_KEY],
                "type": mappings.MIME_GEOJSON,
                "title": f"STAC item of {data_row[mappings.TITLE_KEY]}",
            }
            for _, data_row in data.iterrows()
        ],
        "item_assets": {
            "target": {
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": "Calibration images of heliostats",
            }
        },
    }


def make_calibration_item(image: int, heliostat_data: pd.Series) -> Dict[str, Any]:
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
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [
            "view",
            f"{mappings.CSP_SCHEMA}",
        ],
        "id": f"{image}",
        "type": "Feature",
        "title": f"Calibration image from heliostat {heliostat_data[mappings.HELIOSTAT_ID]} for image {image}",
        "description": f"Images of focused sunlight on the calibration target from heliostat "
        f"{heliostat_data[mappings.HELIOSTAT_ID]} for image{image}",
        "collection": mappings.CALIBRATION_COLLECTION_ID
        % heliostat_data[mappings.HELIOSTAT_ID],
        "geometry": {
            "type": "Point",
            "coordinates": [mappings.POWER_PLANT_LON, mappings.POWER_PLANT_LAT],
        },
        "bbox": [
            mappings.POWER_PLANT_LON,
            mappings.POWER_PLANT_LAT,
            mappings.POWER_PLANT_LON,
            mappings.POWER_PLANT_LAT,
        ],
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
        "view:sun_elevation": heliostat_data[mappings.SUN_ELEVATION],
        "csp:gppd_id": mappings.POWER_PLANT_GPPD_ID,
        "csp:heliostats": [
            {
                "csp:heliostat_id": heliostat_data[mappings.HELIOSTAT_ID],
                "csp:heliostat_motors": [
                    heliostat_data[mappings.AXIS1_MOTOR],
                    heliostat_data[mappings.AXIS2_MOTOR],
                ],
            }
        ],
        "csp:target_id": heliostat_data[mappings.CALIBRATION_TARGET],
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
                "href": mappings.CALIBRATION_COLLECTION_URL
                % heliostat_data[mappings.HELIOSTAT_ID],
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.CALIBRATION_COLLECTION_URL
                % heliostat_data[mappings.HELIOSTAT_ID],
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "target": {
                "href": f"./{image}.png",
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": f"Calibration image of heliostat with id {image}",
            }
        },
    }
