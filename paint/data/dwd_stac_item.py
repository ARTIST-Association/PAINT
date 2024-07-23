from typing import Any, Dict

import pandas as pd

import paint.util.paint_mappings as mappings


def make_dwd_item(
    data: pd.Series,
) -> Dict[str, Any]:
    """
    Generate a STAC item for the DWD weather data.

    Parameters
    ----------
    data : pd.Series
        The metadata for the DWD weather data file.

    Returns
    -------
    dict[str, Any]
        The STAC item data as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": "dwd-weather",
        "type": "Feature",
        "title": "Weather data from the DWD",
        "description": f"Weather data from the DWD station ID {data[mappings.DWD_STATION_ID]}, i.e. "
        f"{data[mappings.DWD_STATION_NAME]}.",
        "collection": mappings.WEATHER_COLLECTION_ID,
        "geometry": {
            "type": "Point",
            "coordinates": [
                data[mappings.LATITUDE_KEY],
                data[mappings.LONGITUDE_KEY],
                data[mappings.ELEVATION],
            ],
        },
        "bbox": [
            data[mappings.LATITUDE_KEY],
            data[mappings.LONGITUDE_KEY],
            data[mappings.ELEVATION],
            data[mappings.LATITUDE_KEY],
            data[mappings.LONGITUDE_KEY],
            data[mappings.ELEVATION],
        ],
        "properties": {
            "datetime": "null",
        },
        "start_datetime": data[mappings.DWD_START],
        "end_datetime": data[mappings.DWD_END],
        "links": [
            {
                "rel": "self",
                "href": f"./{mappings.DWD_STAC_NAME}",
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
            "target": {
                "href": "./dwd-weather.h5",
                "roles": ["data"],
                "type": mappings.MIME_HDF5,
                "title": "Weather data from the DWD",
            }
        },
    }
