import deepdiff
import pandas as pd
import pytest

import paint.data.catalog_stac
import paint.util.paint_mappings


@pytest.fixture
def catalog_data():
    """
    Make a fixture with data for generating the catalog.

    Returns
    -------
    pd.DataFrame
       The test fixture.
    """
    data = {
        "HeliostatId": ["AA23", "AA24", "AA25", "AA26"],
        "CreatedAt": [
            "2021-07-20 07:09:29",
            "2021-07-20 07:09:33",
            "2021-07-20 07:09:37",
            "2021-07-20 07:09:41",
        ],
    }
    df = pd.DataFrame(data)
    df = df.set_index("HeliostatId")
    return df


def test_make_catalog(catalog_data: pd.DataFrame) -> None:
    """Test STAC catalog generation."""
    catalog = paint.data.catalog_stac.make_catalog(data=catalog_data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "WRI1030197-catalog",
        "type": "Catalog",
        "title": "Operational data of concentrating solar power plant WRI1030197",
        "description": "Calibration images, deflectometry measurements, heliostat properties, and weather data",
        "links": [
            {
                "rel": "self",
                "href": "Insert/URL/Here",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": "Insert/URL/Here",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "child",
                "href": "INSERT/SOMETHING/HERE/weather-collection-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the STAC collection containing the weather data",
            },
            {
                "rel": "child",
                "href": "INSERT/SOMETHING/HERE/AA23-heliostat-catalog-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA23",
            },
            {
                "rel": "child",
                "href": "INSERT/SOMETHING/HERE/AA24-heliostat-catalog-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA24",
            },
            {
                "rel": "child",
                "href": "INSERT/SOMETHING/HERE/AA25-heliostat-catalog-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA25",
            },
            {
                "rel": "child",
                "href": "INSERT/SOMETHING/HERE/AA26-heliostat-catalog-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA26",
            },
        ],
    }

    assert not deepdiff.DeepDiff(catalog, expected)
