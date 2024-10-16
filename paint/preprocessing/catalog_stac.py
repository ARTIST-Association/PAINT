from typing import Any

import paint.util.paint_mappings as mappings


def make_catalog(data: list) -> dict[str, Any]:
    """
    Generate the catalog STAC.

    Parameters
    ----------
    data : list
        A list of heliostats.

    Returns
    -------
    dict[str, Any]
        The STAC catalog as dictionary
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.CATALOG_ID,
        "type": mappings.CATALOG,
        "title": f"Operational preprocessing of concentrating solar power plant {mappings.POWER_PLANT_GPPD_ID}",
        "description": "Calibration images, deflectometry measurements, heliostat properties, and weather preprocessing",
        "links": [
            {
                "rel": "self",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "child",
                "href": mappings.WEATHER_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the STAC collection containing the weather preprocessing",
            },
            {
                "rel": "child",
                "href": mappings.TOWER_STAC_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the STAC item containing the tower measurement preprocessing",
            },
        ]
        + [
            {
                "rel": "child",
                "href": mappings.HELIOSTAT_CATALOG_URL % (helio_id, helio_id),
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the STAC catalog containing preprocessing for heliostat "
                f"{helio_id}",
            }
            for helio_id in data
        ],
    }
