from typing import Any

import paint.util.paint_mappings as mappings


def make_heliostat_catalog(
    heliostat_id: str,
    include_deflectometry: bool,
    include_calibration: bool,
    include_properties: bool,
) -> dict[str, Any]:
    """
    Generate a catalog for each heliostat STAC.

    Parameters
    ----------
    heliostat_id : str
        The heliostat ID for the considered heliostat.
    include_deflectometry : bool
        Whether the deflectometry collection is included for this heliostat.
    include_calibration : bool
        Whether the calibration collection is included for this heliostat.
    include_properties : bool
        Whether the properties collection is included for this heliostat.

    Returns
    -------
    dict[str, Any]
        The STAC catalog as dictionary
    """
    if include_deflectometry and include_calibration and include_properties:
        description = (
            "Calibration images, deflectometry measurements, and heliostat properties"
        )
    elif include_deflectometry and include_calibration and not include_properties:
        description = "Calibration images and deflectometry measurements"
    elif include_deflectometry and not include_calibration and include_properties:
        description = "Deflectometry measurements and heliostat properties"
    elif include_deflectometry and not include_calibration and not include_properties:
        description = "Deflectometry measurements"
    elif not include_deflectometry and not include_calibration and include_properties:
        description = "Heliostat properties"
    elif not include_deflectometry and include_calibration and not include_properties:
        description = "Calibration images"
    elif not include_deflectometry and include_calibration and include_properties:
        description = "Calibration images and heliostat properties"
    else:
        raise ValueError("This heliostat doesn't seem to have any data!")

    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [],
        "id": mappings.HELIOSTAT_CATALOG_ID % heliostat_id,
        "type": mappings.CATALOG,
        "title": f"Operational data for the heliostat {heliostat_id}",
        "description": description,
        "links": [
            {
                "rel": "self",
                "href": mappings.HELIOSTAT_CATALOG_URL % (heliostat_id, heliostat_id),
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC catalog file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to the parent catalog",
            },
            *(
                [
                    {
                        "rel": "child",
                        "href": mappings.DEFLECTOMETRY_COLLECTION_URL
                        % (heliostat_id, heliostat_id),
                        "type": mappings.MIME_GEOJSON,
                        "title": "Reference to the STAC collection containing the deflectometry data",
                    }
                ]
                if include_deflectometry
                else []
            ),
            *(
                [
                    {
                        "rel": "child",
                        "href": mappings.CALIBRATION_COLLECTION_URL
                        % (heliostat_id, heliostat_id),
                        "type": mappings.MIME_GEOJSON,
                        "title": "Reference to the STAC collection containing the calibration data",
                    }
                ]
                if include_calibration
                else []
            ),
            *(
                [
                    {
                        "rel": "child",
                        "href": mappings.HELIOSTAT_PROPERTIES_COLLECTION_URL
                        % (heliostat_id, heliostat_id),
                        "type": mappings.MIME_GEOJSON,
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    }
                ]
                if include_properties
                else []
            ),
        ],
    }
