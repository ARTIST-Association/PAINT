from typing import Any, Dict

import pandas as pd

import paint.util.paint_mappings as mappings


def make_weather_collection(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a weather STAC collection.

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe containing all weather metadata.

    Returns
    -------
    dict[str, Any]
        The STAC collection as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.WEATHER_COLLECTION_ID,
        "type": mappings.COLLECTION,
        "title": "All weather measurements",
        "description": "All weather measurements",
        "keywords": ["weather"],
        "license": mappings.LICENSE,
        "providers": [mappings.DLR, mappings.KIT],
        "extent": {
            "spatial": {
                "bbox": [
                    data[mappings.LATITUDE_KEY].min(),
                    data[mappings.LONGITUDE_KEY].min(),
                    int(data[mappings.ELEVATION].min()),
                    data[mappings.LATITUDE_KEY].max(),
                    data[mappings.LONGITUDE_KEY].max(),
                    int(data[mappings.ELEVATION].max()),
                ]
            },
            "temporal": {
                "interval": [
                    data[mappings.DWD_START].min(),
                    data[mappings.DWD_END].max(),
                ]
            },
        },
        "summaries": {
            "datetime": {
                "minimum": data[mappings.DWD_START].min(),
                "maximum": data[mappings.DWD_END].max(),
            },
        },
        "links": [
            mappings.LICENSE_LINK,
            {
                "rel": "self",
                "href": mappings.WEATHER_COLLECTION_URL,
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
                "href": mappings.WEATHER_COLLECTION_FILE,
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
