from typing import Any, Dict

import paint.util.paint_mappings as mappings


# TODO: Fix, so that only the links are saved that are actually there!
def make_heliostat_catalog(heliostat_id: str) -> Dict[str, Any]:
    """
    Generate a catalog for each heliostat STAC.

    Parameters
    ----------
    heliostat_id : str
        The heliostat ID for the considered heliostat.

    Returns
    -------
    dict[str, Any]
        The STAC catalog as dictionary
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.HELIOSTAT_CATALOG_ID % heliostat_id,
        "type": mappings.CATALOG,
        "title": f"Operational data for the heliostat {heliostat_id}",
        "description": "Calibration images, deflectometry measurements, heliostat properties, and weather data",
        "links": [
            {
                "rel": "self",
                "href": mappings.HELIOSTAT_CATALOG_URL % heliostat_id,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC catalog file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the parent catalog",
            },
            {
                "rel": "child",
                "href": mappings.DEFLECTOMETRY_COLLECTION_URL % heliostat_id,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the STAC collection containing the deflectometry data",
            },
            {
                "rel": "child",
                "href": mappings.CALIBRATION_COLLECTION_URL % heliostat_id,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the STAC collection containing the calibration data",
            },
            {
                "rel": "child",
                "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL % heliostat_id,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the STAC collection containing the heliostat properties",
            },
        ],
    }