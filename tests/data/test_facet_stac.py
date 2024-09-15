from typing import Tuple

import deepdiff
import pandas as pd
import pytest

from paint.data.facet_stac import make_facet_item


@pytest.fixture
def facet_item_data() -> Tuple[str, pd.Series]:
    """
    Make a fixture with data for generating a facet item.

    Returns
    -------
    str
        The heliostat ID.
    pd.Series
        The data for the facet stac item.
    """
    data = {
        "East": 13.2,
        "North": 154.7,
        "Altitude": 88.66962,
        "HeightAboveGround": 1.66962,
        "CreatedAt": "2023-09-18Z11:39:25Z",
    }
    return "AY39", pd.Series(data)


def test_make_facet_item(facet_item_data: Tuple[str, pd.Series]) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    facet_item_data : Tuple[str, pd.Series]
        The test fixture.
    """
    heliostat_key, data = facet_item_data
    assert isinstance(heliostat_key, str)
    item = make_facet_item(heliostat_key=heliostat_key, heliostat_data=data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "AY39-facet_properties",
        "type": "Feature",
        "title": "Facet properties of AY39",
        "description": "The facet properties, including canting and translation vectors for heliosat AY39",
        "collection": "AY39-heliostat_properties-collection",
        "geometry": {
            "type": "Point",
            "coordinates": [50.914686955478864, 6.387702537483708, 88.66962],
        },
        "bbox": [
            50.914686955478864,
            6.387702537483708,
            88.66962,
            50.914686955478864,
            6.387702537483708,
            88.66962,
        ],
        "properties": {
            "datetime": "2023-09-18Z11:39:25Z",
            "created": "2023-09-18Z11:39:25Z",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/AY39/Properties/AY39-facet_properties-stac.json",
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
                "href": "https://paint-database.org/WRI1030197/AY39/Properties/AY39-heliostat_properties-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": "https://paint-database.org/WRI1030197/AY39/Properties/AY39-heliostat_properties-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "facet_properties": {
                "href": "https://paint-database.org/WRI1030197/AY39/Properties/AY39-facet_properties.json",
                "roles": ["data"],
                "type": "application/geo+json",
                "title": "Facet properties of AY39",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)
