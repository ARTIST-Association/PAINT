from typing import Any

import pandas as pd

import paint.util.paint_mappings as mappings


def make_calibration_collection(
    heliostat_id: str, data: pd.DataFrame
) -> dict[str, Any]:
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
        "stac_extensions": [],
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
                    data[mappings.LATITUDE_MIN_KEY].min(),
                    data[mappings.LONGITUDE_MIN_KEY].min(),
                    data[mappings.ELEVATION_MIN].min(),
                    data[mappings.LATITUDE_MAX_KEY].max(),
                    data[mappings.LONGITUDE_MAX_KEY].max(),
                    data[mappings.ELEVATION_MAX].max(),
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
                "href": mappings.CALIBRATION_COLLECTION_URL
                % (heliostat_id, heliostat_id),
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
                "href": mappings.CALIBRATION_COLLECTION_URL
                % (heliostat_id, heliostat_id),
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


def make_calibration_item(image: int, heliostat_data: pd.Series) -> dict[str, Any]:
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
        "stac_extensions": [mappings.VIEW_EXTENSION, mappings.PROCESSING_EXTENSION],
        "id": f"{image}",
        "type": "Feature",
        "title": f"Calibration data from heliostat {heliostat_data[mappings.HELIOSTAT_ID]} for image {image}",
        "description": f"Raw and cropped image of focused sunlight on the calibration target from heliostat "
        f"{heliostat_data[mappings.HELIOSTAT_ID]} for image {image} with associated motor positions",
        "collection": mappings.CALIBRATION_COLLECTION_ID
        % heliostat_data[mappings.HELIOSTAT_ID],
        "geometry": {
            "type": "Point",
            "coordinates": mappings.CALIBRATION_TARGET_TO_COORDINATES[
                heliostat_data[mappings.CALIBRATION_TARGET]
            ],
        },
        "bbox": mappings.CALIBRATION_TARGET_TO_BOUNDING_BOX[
            heliostat_data[mappings.CALIBRATION_TARGET]
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
                "href": f"{mappings.URL_BASE}/{heliostat_data[mappings.HELIOSTAT_ID]}/{mappings.SAVE_CALIBRATION}/{image}-stac.json",
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the entire catalogue for {mappings.POWER_PLANT_GPPD_ID}",
            },
            {
                "rel": "parent",
                "href": mappings.CALIBRATION_COLLECTION_URL
                % (
                    heliostat_data[mappings.HELIOSTAT_ID],
                    heliostat_data[mappings.HELIOSTAT_ID],
                ),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.CALIBRATION_COLLECTION_URL
                % (
                    heliostat_data[mappings.HELIOSTAT_ID],
                    heliostat_data[mappings.HELIOSTAT_ID],
                ),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            mappings.CALIBRATION_RAW_IMAGE_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_data[mappings.HELIOSTAT_ID]}/{mappings.SAVE_CALIBRATION}/{image}_raw.png",
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": f"Raw calibration image with id {image}",
            },
            mappings.CALIBRATION_CROPPED_IMAGE_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_data[mappings.HELIOSTAT_ID]}/{mappings.SAVE_CALIBRATION}/{image}.png",
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": f"Cropped calibration image with id {image}",
                "processing:lineage": "Target cropping through template matching",
                "processing:software": f"PAINT target cropper ({mappings.PAINT_REPO_URL})",
            },
            mappings.CALIBRATION_PROPERTIES_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_data[mappings.HELIOSTAT_ID]}/{mappings.SAVE_CALIBRATION}/{mappings.CALIBRATION_PROPERTIES_NAME % image}.json",
                "roles": ["metadata"],
                "type": mappings.MIME_GEOJSON,
                "title": f"Calibration properties for the calibration image id {image}",
                "processing:lineage": "Focal spot extraction",
                "processing:software": f"{mappings.HELIOS_KEY}, {mappings.UTIS_KEY} ({mappings.UTIS_URL})",
            },
        },
    }
