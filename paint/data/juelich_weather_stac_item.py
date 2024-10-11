from typing import Any

import pandas as pd

import paint.util.paint_mappings as mappings


def make_juelich_weather_item(
    data: pd.Series,
    month_group: str,
) -> dict[str, Any]:
    """
    Generate a STAC item for the Juelich weather data.

    Parameters
    ----------
    data : pd.Series
        Metadata for the Juelich weather data file.
    month_group : str
        Considered month group.

    Returns
    -------
    dict[str, Any]
        The STAC item data as dictionary.
    """
    resource = mappings.JUELICH_FILE_NAME % month_group
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": resource,
        "type": "Feature",
        "title": f"Weather data from Juelich for {month_group}",
        "description": f"Weather data from the Juelich weather station for {month_group}",
        "collection": mappings.WEATHER_COLLECTION_ID,
        "geometry": {
            "type": "Point",
            "coordinates": [
                mappings.JUELICH_WEATHER_LAT,
                mappings.JUELICH_WEATHER_LON,
                mappings.JUELICH_WEATHER_ALTITUDE,
            ],
        },
        "bbox": [
            mappings.JUELICH_WEATHER_LAT,
            mappings.JUELICH_WEATHER_LON,
            mappings.JUELICH_WEATHER_ALTITUDE,
            mappings.JUELICH_WEATHER_LAT,
            mappings.JUELICH_WEATHER_LON,
            mappings.JUELICH_WEATHER_ALTITUDE,
        ],
        "properties": {
            "datetime": "null",
        },
        "start_datetime": data[mappings.JUELICH_START],
        "end_datetime": data[mappings.JUELICH_END],
        "links": [
            {
                "rel": "self",
                "href": f"{mappings.URL_BASE}/{mappings.SAVE_WEATHER}/{mappings.JUELICH_STAC_NAME % month_group}.json",
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
                "href": mappings.WEATHER_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.WEATHER_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            mappings.WEATHER_DATA_KEY: {
                "href": f"{mappings.URL_BASE}/{mappings.SAVE_WEATHER}/{mappings.JUELICH_FILE_NAME % month_group}.h5",
                "roles": ["data"],
                "type": mappings.MIME_HDF5,
                "title": f"Weather data from the Juelich weather station for {month_group}",
            }
        },
    }
