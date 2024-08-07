from typing import Any, Dict

import pandas as pd

import paint.util.paint_mappings as mappings


def make_properties_collection(heliostat_id: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a heliostat properties STAC collection.

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
        "id": mappings.HELIOSTAT_PROPERTIES_COLLECTION_ID % heliostat_id,
        "type": mappings.COLLECTION,
        "title": f"Heliostat properties data for {heliostat_id}",
        "description": f"All heliostat properties, including the facet properties and kinematic properties for "
        f"heliostat {heliostat_id}",
        "keywords": ["csp", "facet", "kinematic", "properties"],
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
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL % heliostat_id,
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
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL % heliostat_id,
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
