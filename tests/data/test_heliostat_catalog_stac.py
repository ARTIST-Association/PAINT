from typing import Any

import deepdiff
import pytest

from paint.data.heliostat_catalog_stac import make_heliostat_catalog


@pytest.mark.parametrize(
    "heliostat_id, include_deflectometry, expected",
    [
        (
            "AA23",
            True,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA23-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA23",
                "description": "Calibration images, deflectometry measurements, heliostat properties, and weather data",
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
                        "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-heliostat_properties-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    },
                ],
            },
        ),
        (
            "AA41",
            False,
            {
                "stac_version": "1.0.0",
                "stac_extensions": [],
                "id": "AA41-heliostat-catalog",
                "type": "Catalog",
                "title": "Operational data for the heliostat AA41",
                "description": "Calibration images, deflectometry measurements, heliostat properties, and weather data",
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
                        "href": "https://paint-database.org/WRI1030197/AA41/Properties/AA41-heliostat_properties-collection-stac.json",
                        "type": "application/geo+json",
                        "title": "Reference to the STAC collection containing the heliostat properties",
                    },
                ],
            },
        ),
    ],
)
def test_make_heliostat_catalog(
    heliostat_id: str, include_deflectometry: bool, expected: dict[str, Any]
) -> None:
    """Test STAC heliostat catalog generation."""
    catalog = make_heliostat_catalog(
        heliostat_id=heliostat_id, include_deflectometry=include_deflectometry
    )

    assert not deepdiff.DeepDiff(catalog, expected)
