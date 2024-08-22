from typing import Any, Dict

import pandas as pd

import paint.util.paint_mappings as mappings


def make_juelich_weather_item(
    data: pd.Series,
) -> Dict[str, Any]:
    """
    Generate a STAC item for the Juelich weather data.

    Parameters
    ----------
    data : pd.Series
        The metadata for the Juelich weather data file.

    Returns
    -------
    dict[str, Any]
        The STAC item data as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": "juelich-weather",
        "type": "Feature",
        "title": "Weather data from Juelich",
        "description": "Weather data from the Juelich weather station",
        "collection": mappings.WEATHER_COLLECTION_ID,
        "geometry": {
            "type": "Point",
            "coordinates": [
                mappings.JUELICH_WEATHER_LAT,
                mappings.JEULICH_WEATHER_LON,
                mappings.JEULICH_WEATHER_ALTITUDE,
            ],
        },
        "bbox": [
            mappings.JUELICH_WEATHER_LAT,
            mappings.JEULICH_WEATHER_LON,
            mappings.JEULICH_WEATHER_ALTITUDE,
            mappings.JUELICH_WEATHER_LAT,
            mappings.JEULICH_WEATHER_LON,
            mappings.JEULICH_WEATHER_ALTITUDE,
        ],
        "properties": {
            "datetime": "null",
        },
        "start_datetime": data[mappings.JUELICH_START],
        "end_datetime": data[mappings.JUELICH_END],
        "links": [
            {
                "rel": "self",
                "href": f"./{mappings.JUELICH_STAC_NAME}",
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
                "href": mappings.WEATHER_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": mappings.WEATHER_COLLECTION_FILE,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            mappings.WEATHER_DATA_KEY: {
                "href": "./juelich-weather.h5",
                "roles": ["data"],
                "type": mappings.MIME_HDF5,
                "title": "Weather data from the Juelich weather station",
            }
        },
    }
