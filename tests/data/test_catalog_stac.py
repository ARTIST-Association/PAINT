import deepdiff
import pytest

import paint.data.catalog_stac
import paint.util.paint_mappings


@pytest.fixture
def catalog_data() -> list[str]:
    """
    Make a fixture with data for generating the catalog.

    Returns
    -------
    List[str]
       The test fixture.
    """
    return ["AA23", "AA24", "AA25", "AA26"]


def test_make_catalog(catalog_data: list[str]) -> None:
    """
    Test STAC catalog generation.

    Parameters
    ----------
    catalog_data : List[str]
        The test fixture.
    """
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
                "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "child",
                "href": "https://paint-database.org/WRI1030197/Weather/weather-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the STAC collection containing the weather data",
            },
            {
                "rel": "child",
                "href": "https://paint-database.org/WRI1030197/juelich-tower-measurements-item-stac",
                "type": "application/geo+json",
                "title": "Reference to the STAC item containing the tower measurement data",
            },
            {
                "rel": "child",
                "href": "https://paint-database.org/WRI1030197/AA23/AA23-heliostat-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA23",
            },
            {
                "rel": "child",
                "href": "https://paint-database.org/WRI1030197/AA24/AA24-heliostat-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA24",
            },
            {
                "rel": "child",
                "href": "https://paint-database.org/WRI1030197/AA25/AA25-heliostat-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA25",
            },
            {
                "rel": "child",
                "href": "https://paint-database.org/WRI1030197/AA26/AA26-heliostat-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the STAC catalog containing data for heliostat AA26",
            },
        ],
    }

    assert not deepdiff.DeepDiff(catalog, expected)
