from typing import Any, Dict, Tuple

import pandas as pd

import paint.util.paint_mappings as mappings
from paint.util import add_offset_to_lat_lon
from paint.util.utils import to_utc_single


def make_properties_collection(heliostat_id: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a heliostat properties STAC collection.

    Parameters
    ----------
    heliostat_id: str
        The heliostat ID of the heliostat containing the collection.
    data: pd.DataFrame
        The dataframe containing all properties metadata.

    Returns
    -------
    dict[str, Any]
        The STAC collection as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.HELIOSTAT_PROPERTIES_COLLECTION_ID % heliostat_id,
        "type": mappings.COLLECTION,
        "title": f"Heliostat properties data for {heliostat_id}",
        "description": f"All heliostat properties for heliostat {heliostat_id}",
        "keywords": [
            "csp",
            "facet",
            "kinematic",
            "position",
            "renovation",
            "properties",
        ],
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
                    data[mappings.CREATED_AT].min(),
                    data[mappings.CREATED_AT].max(),
                ]
            },
        },
        "summaries": {
            "datetime": {
                "minimum": data[mappings.CREATED_AT].min(),
                "maximum": data[mappings.CREATED_AT].max(),
            },
        },
        "links": [
            mappings.LICENSE_LINK,
            {
                "rel": "self",
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL
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
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL
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


def make_properties_item(
    heliostat_key: str,
    heliostat_data: pd.Series,
) -> Tuple[Tuple[float, float], Dict[str, Any]]:
    """
    Generate a STAC item for the heliostat properties.

    Parameters
    ----------
    heliostat_key: str
        The ID of the heliostat which was measured.
    heliostat_data: pd.Series.
        The metadata for the heliostat.

    Returns
    -------
    Tuple[float, float]
        The latitude and longitude coordinates of the heliostat.
    Dict[str, Any]
        The STAC item data as dictionary.
    """
    resource = heliostat_key + "-heliostat_properties"
    lat_lon = add_offset_to_lat_lon(
        east_offset_m=heliostat_data[mappings.EAST_KEY],
        north_offset_m=heliostat_data[mappings.NORTH_KEY],
    )
    return lat_lon, {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": f"{resource}",
        "type": "Feature",
        "title": f"Heliostat properties of {heliostat_key}",
        "description": f"The heliostat properties for heliostat {heliostat_key}. This includes the position of the"
        f"heliostat, the kinematic applied, the facet properties, and the renovation date if the"
        f"heliostat was renovated",
        "collection": mappings.HELIOSTAT_PROPERTIES_COLLECTION_ID % heliostat_key,
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
            "datetime": to_utc_single(heliostat_data[mappings.CREATED_AT]),
            "created": to_utc_single(heliostat_data[mappings.CREATED_AT]),
        },
        "links": [
            {
                "rel": "self",
                "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_PROPERTIES}/{resource}-stac.json",
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
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL
                % (heliostat_key, heliostat_key),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL
                % (heliostat_key, heliostat_key),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            mappings.HELIOSTAT_PROPERTIES_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_PROPERTIES}/"
                f"{mappings.HELIOSTAT_PROPERTIES_SAVE_NAME % heliostat_key}",
                "roles": ["data"],
                "type": mappings.MIME_GEOJSON,
                "title": f"Heliostat properties for heliostat {heliostat_key}",
            }
        },
    }
