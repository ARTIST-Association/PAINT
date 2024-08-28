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
        "stac_extensions": [mappings.ITEM_ASSETS_SCHEMA],
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
                    data[mappings.LATITUDE_KEY].min(),
                    data[mappings.LONGITUDE_KEY].min(),
                    data[mappings.ELEVATION].min(),
                    data[mappings.LATITUDE_KEY].max(),
                    data[mappings.LONGITUDE_KEY].max(),
                    data[mappings.ELEVATION].max(),
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
        ],
        "id": f"{image}",
        "type": "Feature",
        "title": f"Calibration data from heliostat {heliostat_data[mappings.HELIOSTAT_ID]} for image {image}",
        "description": f"Image of focused sunlight on the calibration target from heliostat "
        f"{heliostat_data[mappings.HELIOSTAT_ID]} for image {image} with associated motor positions",
        "collection": mappings.CALIBRATION_COLLECTION_ID
        % heliostat_data[mappings.HELIOSTAT_ID],
        "geometry": {
            "type": "Point",
            "coordinates": [
                mappings.CALIBRATION_TARGET_TO_COORDINATES[
                    heliostat_data[mappings.CALIBRATION_TARGET]
                ][0],
                mappings.CALIBRATION_TARGET_TO_COORDINATES[
                    heliostat_data[mappings.CALIBRATION_TARGET]
                ][1],
                mappings.CALIBRATION_TARGET_TO_COORDINATES[
                    heliostat_data[mappings.CALIBRATION_TARGET]
                ][2],
            ],
        },
        "bbox": [
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][0],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][1],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][2],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][0],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][1],
            mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ][2],
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
        "links": [
            {
                "rel": "self",
                "href": f"./{image}-stac.json",
                "type": mappings.MIME_GEOJSON,
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
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.CALIBRATION_COLLECTION_URL
                % heliostat_data[mappings.HELIOSTAT_ID],
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            mappings.CALIBRATION_TARGET_KEY: {
                "href": f"./{image}.png",
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": f"Calibration image with id {image}",
            },
            mappings.CALIBRATION_MOTOR_POS_KEY: {
                "href": f"./{mappings.MOTOR_POS_NAME % (heliostat_data[mappings.HELIOSTAT_ID], image)}.json",
                "roles": ["metadata"],
                "type": mappings.MIME_GEOJSON,
                "title": f"Motor positions for the calibration image id {image}",
            },
        },
    }
