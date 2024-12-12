from typing import Any

import deepdiff
import pytest

from paint.preprocessing.heliostat_catalog_stac import make_heliostat_catalog


@pytest.mark.parametrize(
    "heliostat_id, include_deflectometry, include_calibration, include_properties, expected",
    [
        (
            "AA23",
            True,
            True,
            True,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA23-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA23",
                "description": "Calibration images, deflectometry measurements, and heliostat properties",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://paint-database.org/WRI1030197/AA23/AA23-heliostat-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to this STAC catalog file",
                    },
                    {
                        "rel": "root",
                        "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the parent catalog",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA23/Deflectometry/AA23-deflectometry-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the deflectometry data",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA23/Calibration/AA23-calibration-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the calibration data",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-heliostat-properties-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    },
                ],
            },
        ),
        (
            "AA41",
            False,
            True,
            True,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA41-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA41",
                "description": "Calibration images and heliostat properties",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://paint-database.org/WRI1030197/AA41/AA41-heliostat-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to this STAC catalog file",
                    },
                    {
                        "rel": "root",
                        "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the parent catalog",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Calibration/AA41-calibration-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the calibration data",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Properties/AA41-heliostat-properties-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    },
                ],
            },
        ),
        (
            "AA41",
            False,
            False,
            True,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA41-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA41",
                "description": "Heliostat properties",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://paint-database.org/WRI1030197/AA41/AA41-heliostat-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to this STAC catalog file",
                    },
                    {
                        "rel": "root",
                        "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the parent catalog",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Properties/AA41-heliostat-properties-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    },
                ],
            },
        ),
        (
            "AA41",
            False,
            True,
            False,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA41-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA41",
                "description": "Calibration images",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://paint-database.org/WRI1030197/AA41/AA41-heliostat-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to this STAC catalog file",
                    },
                    {
                        "rel": "root",
                        "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the parent catalog",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Calibration/AA41-calibration-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the calibration data",
                    },
                ],
            },
        ),
        (
            "AA41",
            True,
            False,
            True,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA41-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA41",
                "description": "Deflectometry measurements and heliostat properties",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://paint-database.org/WRI1030197/AA41/AA41-heliostat-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to this STAC catalog file",
                    },
                    {
                        "rel": "root",
                        "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the parent catalog",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Deflectometry/AA41-deflectometry-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the deflectometry data",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Properties/AA41-heliostat-properties-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    },
                ],
            },
        ),
        (
            "AA41",
            True,
            True,
            False,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA41-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA41",
                "description": "Calibration images and deflectometry measurements",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://paint-database.org/WRI1030197/AA41/AA41-heliostat-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to this STAC catalog file",
                    },
                    {
                        "rel": "root",
                        "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the parent catalog",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Deflectometry/AA41-deflectometry-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the deflectometry data",
                    },
                    {
                        "rel": "child",
                        "href": "https://paint-database.org/WRI1030197/AA41/Calibration/AA41-calibration-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the calibration data",
                    },
                ],
            },
        ),
    ],
)
def test_make_heliostat_catalog(
    heliostat_id: str,
    include_deflectometry: bool,
    include_calibration: bool,
    include_properties: bool,
    expected: dict[str, Any],
) -> None:
    """
    Test STAC heliostat catalog generation.

    Parameters
    ----------
    heliostat_id : str
        ID of the heliostat for which a STAC is generated.
    include_deflectometry : bool
        Whether to include deflectometry measurements.
    include_calibration : bool
        Whether to include calibration measurements.
    include_properties : bool
        Whether to include heliostat properties.
    """
    catalog = make_heliostat_catalog(
        heliostat_id=heliostat_id,
        include_deflectometry=include_deflectometry,
        include_calibration=include_calibration,
        include_properties=include_properties,
    )

    assert not deepdiff.DeepDiff(catalog, expected)
