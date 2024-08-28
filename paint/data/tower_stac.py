from typing import Any, Dict

import numpy as np

import paint.util.paint_mappings as mappings


def make_tower_item(
    extreme_coordinates: Dict[str, np.ndarray],
) -> Dict[str, Any]:
    """
    Generate a STAC item for the tower metadata JSON.

    Parameters
    ----------
    extreme_coordinates : Dict[str, np.ndarray]
        Contains the max and min for each of the latitude, longitude, and elevation coordinates from the tower.

    Returns
    -------
    dict[str, Any]
        The STAC item data as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": f"{mappings.TOWER_FILE_NAME}",
        "type": "Feature",
        "title": "The coordinates of different targets from the the Juelich solar tower.",
        "description": "The latitude, longitude, and elevation coordinates for the center and corners of all "
        "calibration targets and the receiver for the Juelich solar tower.",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                extreme_coordinates[mappings.LATITUDE_KEY].min(),
                extreme_coordinates[mappings.LATITUDE_KEY].min(),
                extreme_coordinates[mappings.ELEVATION].min(),
                extreme_coordinates[mappings.LATITUDE_KEY].max(),
                extreme_coordinates[mappings.LATITUDE_KEY].max(),
                extreme_coordinates[mappings.ELEVATION].max(),
            ],
        },
        "bbox": [
            extreme_coordinates[mappings.LATITUDE_KEY].min(),
            extreme_coordinates[mappings.LATITUDE_KEY].min(),
            extreme_coordinates[mappings.ELEVATION].min(),
            extreme_coordinates[mappings.LATITUDE_KEY].max(),
            extreme_coordinates[mappings.LATITUDE_KEY].max(),
            extreme_coordinates[mappings.ELEVATION].max(),
        ],
        "properties": {
            "datetime": None,
            "start_datetime": mappings.TOWER_START_DATETIME,
            "end_datetime": mappings.TOWER_END_DATETIME,
            "created": mappings.TOWER_START_DATETIME,
            "updated": mappings.TOWER_END_DATETIME,
        },
        "links": [
            {
                "rel": "self",
                "href": f"./{mappings.TOWER_STAC_NAME}.json",
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
                "href": f"./{mappings.CATALOGUE_URL}",
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the catalogue for {mappings.POWER_PLANT_GPPD_ID}",
            },
        ],
        "assets": {
            mappings.TOWER_KEY: {
                "href": f"./{mappings.TOWER_FILE_NAME}.json",
                "roles": ["data"],
                "type": mappings.MIME_GEOJSON,
                "title": "Tower measurement properties",
            }
        },
    }
