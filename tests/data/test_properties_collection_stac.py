import deepdiff
import pandas as pd
import pytest

import paint.util.paint_mappings as mappings
from paint.data.properties_collection_stac import make_properties_collection


@pytest.fixture
def properties_collection_data() -> pd.DataFrame:
    """
    Make a fixture with data for generating the heliostat properties collection.

    Returns
    -------
    pd.DataFrame
        The data for the heliostat properties collection as a test fixture.
    """
    # Define the data
    data = {
        "HeliostatId": ["AY39", "AY39"],
        "title": ["kinematic properties for AY39", "facet properties for AY39"],
        "url": [
            "INSERT/SOMETHING/HERE/AY39-kinematic_properties-item-stac.json?download=1",
            "INSERT/SOMETHING/HERE/AY39-facet_properties-item-stac.json?download=1",
        ],
        "CreatedAt": ["2021-12-03Z12:28:26Z", "2023-09-18Z11:39:25Z"],
        "latitude": [50.914686955478864, 50.914686955478864],
        "longitude": [6.387702537483708, 6.387702537483708],
        "Elevation": [88.66962, 88.66962],
    }

    return pd.DataFrame(data)


def test_make_deflectometry_collection(
    properties_collection_data: pd.DataFrame,
) -> None:
    """
    Test the creation of the heliostat properties STAC collection.

    Parameters
    ----------
    properties_collection_data: pd.DataFrame
        The test fixture.
    """
    for heliostat, data in properties_collection_data.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_properties_collection(heliostat_id=heliostat, data=data)

        expected = {
            "stac_version": "1.0.0",
            "stac_extensions": [],
            "id": "AY39-heliostat_properties-collection",
            "type": "Collection",
            "title": "Heliostat properties data for AY39",
            "description": "All heliostat properties, including the facet properties and kinematic properties for heliostat AY39",
            "keywords": ["csp", "facet", "kinematic", "properties"],
            "license": "CDLA-2.0",
            "providers": [
                {
                    "name": "German Aerospace Center (DLR)",
                    "description": "National center for aerospace, energy and transportation research of Germany",
                    "roles": ["licensor", "producer", "processor"],
                    "url": "https://github.com/ARTIST-Association/PAINT/",
                },
                {
                    "name": "Karlsruhe Institute of Technology (KIT)",
                    "description": "Public research center and university in Karlsruhe, Germany",
                    "roles": ["producer", "processor", "host"],
                    "url": "https://github.com/ARTIST-Association/PAINT/",
                },
            ],
            "extent": {
                "spatial": {
                    "bbox": [
                        [
                            50.914686955478864,
                            6.387702537483708,
                            88.66962,
                            50.914686955478864,
                            6.387702537483708,
                            88.66962,
                        ]
                    ]
                },
                "temporal": {
                    "interval": ["2021-12-03Z12:28:26Z", "2023-09-18Z11:39:25Z"]
                },
            },
            "summaries": {
                "datetime": {
                    "minimum": "2021-12-03Z12:28:26Z",
                    "maximum": "2023-09-18Z11:39:25Z",
                }
            },
            "links": [
                {
                    "rel": "license",
                    "href": "https://cdla.dev/permissive-2-0/",
                    "type": "text/html",
                    "title": "Community Data License Agreement – Permissive – Version 2.0",
                },
                {
                    "rel": "self",
                    "href": "INSERT/SOMETHING/HERE/AY39-heliostat_properties-collection-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "Reference to this STAC collection file",
                },
                {
                    "rel": "root",
                    "href": "Insert/URL/Here",
                    "type": "application/geo+json",
                    "title": "Reference to the entire catalogue for WRI1030197",
                },
                {
                    "rel": "collection",
                    "href": "INSERT/SOMETHING/HERE/AY39-heliostat_properties-collection-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "Reference to this STAC collection file",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/AY39-kinematic_properties-item-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "STAC item of kinematic properties for AY39",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/AY39-facet_properties-item-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "STAC item of facet properties for AY39",
                },
            ],
        }

        assert not deepdiff.DeepDiff(
            collection, expected, ignore_numeric_type_changes=True
        )


def test_make_weather_collection_fail() -> None:
    """Test conversion failure on incomplete input data."""
    with pytest.raises(KeyError):
        make_properties_collection("AB123", pd.DataFrame())