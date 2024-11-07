import deepdiff
import pandas as pd
import pytest

import paint.util.paint_mappings as mappings
from paint.preprocessing.properties_stac import (
    make_properties_collection,
    make_properties_item,
)


@pytest.fixture
def properties_collection_data() -> pd.DataFrame:
    """
    Make a fixture with data for generating the heliostat properties collection.

    Returns
    -------
    pd.DataFrame
        The data for the heliostat properties collection as a test fixture.
    """
    # Define the data.
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


def test_make_properties_collection(
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
            "description": "All heliostat properties for heliostat AY39",
            "keywords": [
                "csp",
                "facet",
                "kinematic",
                "position",
                "renovation",
                "properties",
            ],
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
                    "interval": [["2021-12-03Z12:28:26Z", "2023-09-18Z11:39:25Z"]]
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
                    "href": "https://paint-database.org/WRI1030197/AY39/Properties/AY39-heliostat_properties-collection-stac.json",
                    "type": "application/geo+json",
                    "title": "Reference to this STAC collection file",
                },
                {
                    "rel": "root",
                    "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                    "type": "application/geo+json",
                    "title": "Reference to the entire catalogue for WRI1030197",
                },
                {
                    "rel": "collection",
                    "href": "https://paint-database.org/WRI1030197/AY39/Properties/AY39-heliostat_properties-collection-stac.json",
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


@pytest.fixture
def properties_item_data() -> tuple[str, pd.Series]:
    """
    Make a fixture with data for generating a properties item.

    Returns
    -------
    str
        The heliostat ID.
    pd.Series
        The data for the properties STAC item.
    """
    data = {
        "CreatedAt": "2021-07-20 07:09:29",
        "East": -57.2,
        "North": 25.0,
        "Altitude": 88.711,
        "HeightAboveGround": 1.711,
        "FieldId": 1,
        "Type_axis_1": "LINEAR",
        "MinCounts_axis_1": 0,
        "MaxCounts_axis_1": 69296,
        "PulseRatio_axis_1": 154166.666667,
        "A_axis_1": 0,
        "B_axis_1": 0.075005,
        "C_axis_1": 0.335308,
        "D_axis_1": 0.338095,
        "E_axis_1": 0,
        "Reversed_axis_1": 0,
        "AngleK_axis_1": 0.005843,
        "AngleMin_axis_1": 0.004435,
        "AngleMax_axis_1": 1.570796,
        "AngleW_axis_1": 0.025,
        "Type_axis_2": "LINEAR",
        "MinCounts_axis_2": 0,
        "MaxCounts_axis_2": 75451,
        "PulseRatio_axis_2": 154166.666667,
        "A_axis_2": 0,
        "B_axis_2": 0.078887,
        "C_axis_2": 0.340771,
        "D_axis_2": 0.3191,
        "E_axis_2": 0,
        "Reversed_axis_2": 1,
        "AngleK_axis_2": 0.939721,
        "AngleMin_axis_2": -0.95993,
        "AngleMax_axis_2": 0.929079,
        "AngleW_axis_2": 0.025,
    }
    return "AA23", pd.Series(data)


def test_make_properties_item(properties_item_data: tuple[str, pd.Series]) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    properties_item_data : tuple[str, pd.Series]
        The test fixture.
    """
    heliostat_key, data = properties_item_data
    assert isinstance(heliostat_key, str)
    _, item = make_properties_item(heliostat_key=heliostat_key, heliostat_data=data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "AA23-heliostat_properties",
        "type": "Feature",
        "title": "Heliostat properties of AA23",
        "description": "The heliostat properties for heliostat AA23. These include the heliostat position,the kinematic applied, the facet properties, and, if applicable, the renovation date.",
        "collection": "AA23-heliostat_properties-collection",
        "geometry": {
            "type": "Point",
            "coordinates": [50.9136480567095, 6.386990188439183, 88.711],
        },
        "bbox": [
            50.9136480567095,
            6.386990188439183,
            88.711,
            50.9136480567095,
            6.386990188439183,
            88.711,
        ],
        "properties": {
            "datetime": "2021-07-20Z05:09:29Z",
            "created": "2021-07-20Z05:09:29Z",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-heliostat_properties-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the entire catalogue for WRI1030197",
            },
            {
                "rel": "parent",
                "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-heliostat_properties-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-heliostat_properties-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "heliostat_properties": {
                "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-heliostat_properties.json",
                "roles": ["data"],
                "type": "application/geo+json",
                "title": "Heliostat properties for heliostat AA23",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)


def test_make_properties_collection_fail() -> None:
    """Test conversion failure on incomplete input data."""
    with pytest.raises(KeyError):
        make_properties_collection("AB123", pd.DataFrame())
