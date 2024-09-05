from typing import Any, Dict, Tuple

import pandas as pd

import paint.util.paint_mappings as mappings
from paint.util.utils import add_offset_to_lat_lon, to_utc_single


def make_kinematic_item(
    heliostat_key: str,
    heliostat_data: pd.Series,
) -> Tuple[Tuple[float, float], Dict[str, Any]]:
    """
    Generate a STAC item for the heliostat kinematic properties.

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
    resource = heliostat_key + "-kinematic_properties"
    lat_lon = add_offset_to_lat_lon(
        east_offset_m=heliostat_data[mappings.EAST_KEY],
        north_offset_m=heliostat_data[mappings.NORTH_KEY],
    )
    return lat_lon, {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": f"{resource}",
        "type": "Feature",
        "title": f"Kinematic properties of {heliostat_key}",
        "description": f"The kinematic properties that describe the kinematic applied in {heliostat_key}",
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
            lat_lon[0] - mappings.BBOX_LAT_LON_DEVIATION,
            lat_lon[1] - mappings.BBOX_LAT_LON_DEVIATION,
            heliostat_data[mappings.ALTITUDE_KEY] - mappings.BBOX_ALTITUDE_DEVIATION,
            lat_lon[0] + mappings.BBOX_LAT_LON_DEVIATION,
            lat_lon[1] + mappings.BBOX_LAT_LON_DEVIATION,
            heliostat_data[mappings.ALTITUDE_KEY] + mappings.BBOX_ALTITUDE_DEVIATION,
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
            mappings.KINEMATIC_PROPERTIES_KEY: {
                "href": f"{mappings.URL_BASE}/{heliostat_key}/{mappings.SAVE_PROPERTIES}/{resource}.json",
                "roles": ["data"],
                "type": mappings.MIME_GEOJSON,
                "title": f"Kinematic properties of {heliostat_key}",
            }
        },
    }
