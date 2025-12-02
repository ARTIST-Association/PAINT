from typing import Any

import pandas as pd

import paint.util.paint_mappings as mappings
from paint.util import convert_gk_to_lat_lon


def make_deflectometry_collection(
    heliostat_id: str, data: pd.DataFrame
) -> dict[str, Any]:
    """
    Generate a deflectometry STAC collection.

    Parameters
    ----------
    heliostat_id: str
        The heliostat ID of the heliostat containing the collection.
    data: pd.DataFrame
        The dataframe containing all deflectometry metadata.

    Returns
    -------
    dict[str, Any]
        The STAC collection as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.DEFLECTOMETRY_COLLECTION_ID % heliostat_id,
        "type": mappings.COLLECTION,
        "title": f"Deflectometry data for heliostat {heliostat_id}",
        "description": f"All deflectometry data, including raw measurements, filled measurements and results summary "
        f"for heliostat {heliostat_id}",
        "keywords": ["csp", "deflectometry"],
        "license": mappings.LICENSE,
        "providers": [mappings.DLR, mappings.KIT],
        "extent": {
            "spatial": {
                "bbox": [
                    [
                        data[mappings.LATITUDE_KEY].min(),
                        data[mappings.LONGITUDE_KEY].min(),
                        data[mappings.ELEVATION].min(),
                        data[mappings.LATITUDE_KEY].max(),
                        data[mappings.LONGITUDE_KEY].max(),
                        data[mappings.ELEVATION].max(),
                    ]
                ]
            },
            "temporal": {
                "interval": [
                    [
                        data[mappings.CREATED_AT].min(),
                        data[mappings.CREATED_AT].max(),
                    ]
                ]
            },
        },
        "summaries": {
            "datetime": {
                "minimum": data[mappings.CREATED_AT].min(),
                "maximum": data[mappings.CREATED_AT].max(),
            },
            "instruments": mappings.DEFLECTOMETRY_INSTRUMENTS,
        },
        "links": [
            mappings.LICENSE_LINK,
            {
                "rel": "self",
                "href": mappings.DEFLECTOMETRY_COLLECTION_URL
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
                "href": mappings.DEFLECTOMETRY_COLLECTION_URL
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


def make_deflectometry_item(
    heliostat_key: str,
    heliostat_data: pd.Series,
    results_exist: bool,
) -> tuple[tuple[float, float], dict[str, Any]]:
    """
    Generate a STAC item for a deflectometry measurement.

    Parameters
    ----------
    heliostat_key: str
        The ID of the heliostat which was measured.
    heliostat_data : pd.Series
        The metadata for the heliostat.
    results_exist : bool
        Whether the results PDF exists.

    Returns
    -------
    tuple[float, float]
        The latitude and longitude coordinates of the heliostat that being measured.
    dict[str, Any]
        The STAC item data as dictionary.
    """
    resource = (
        heliostat_key
        + "-"
        + heliostat_data[mappings.FILE_CREATED_AT]
        + "-deflectometry"
    )
    lat_lon = convert_gk_to_lat_lon(
        right=mappings.GK_RIGHT_BASE + heliostat_data[mappings.EAST_KEY],
        height=mappings.GK_HEIGHT_BASE + heliostat_data[mappings.NORTH_KEY],
    )
    return lat_lon, {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": f"{resource}",
        "type": "Feature",
        "title": f"Deflectometry measurement of {heliostat_key}",
        "description": f"Measured raw and filled deflectometry data containing point clouds and surface normals for "
        f"heliosat {heliostat_key} and the deflectometry measurement results summary",
        "collection": mappings.DEFLECTOMETRY_COLLECTION_ID % heliostat_key,
        "geometry": {
            "type": "Point",
            "coordinates": [
                lat_lon[0],
                lat_lon[1],
                heliostat_data[mappings.ALTITUDE_KEY],
            ],
        },
        "bbox": [
            lat_lon[0],
            lat_lon[1],
            heliostat_data[mappings.ALTITUDE_KEY],
            lat_lon[0],
            lat_lon[1],
            heliostat_data[mappings.ALTITUDE_KEY],
        ],
        "properties": {
            "datetime": heliostat_data[mappings.CREATED_AT],
            "created": heliostat_data[mappings.CREATED_AT],
            "instruments": f"{mappings.DEFLECTOMETRY_INSTRUMENTS}",
        },
        "links": [
            {
                "rel": "self",
                "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_DEFLECTOMETRY}/{resource}-stac.json",
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
                "href": mappings.DEFLECTOMETRY_COLLECTION_URL
                % (heliostat_key, heliostat_key),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.DEFLECTOMETRY_COLLECTION_URL
                % (heliostat_key, heliostat_key),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            mappings.DEFLECTOMETRY_RAW_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_DEFLECTOMETRY}/{heliostat_key}-{heliostat_data[mappings.FILE_CREATED_AT]}-deflectometry.h5",
                "roles": ["data"],
                "type": mappings.MIME_HDF5,
                "title": f"Raw deflectometry measurement of {heliostat_key} at "
                f"{heliostat_data[mappings.CREATED_AT]}",
            },
            mappings.DEFLECTOMETRY_FILLED_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_DEFLECTOMETRY}/{heliostat_key}-filled-{heliostat_data[mappings.FILE_CREATED_AT]}-deflectometry.h5",
                "roles": ["data"],
                "type": mappings.MIME_HDF5,
                "title": f"Filled deflectometry measurement of {heliostat_key} at "
                f"{heliostat_data[mappings.CREATED_AT]}",
            },
            **(
                {
                    mappings.DEFLECTOMETRY_RESULTS_KEY: {
                        "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_DEFLECTOMETRY}/{heliostat_key}-{heliostat_data[mappings.FILE_CREATED_AT]}-deflectometry-result.pdf",
                        "roles": ["metadata"],
                        "type": mappings.MIME_PDF,
                        "title": f"Summary of deflectometry measurement of {heliostat_key} at "
                        f"{heliostat_data[mappings.CREATED_AT]}",
                    }
                }
                if results_exist
                else {}
            ),
        },
    }
