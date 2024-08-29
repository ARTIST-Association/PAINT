from typing import Tuple

import deepdiff
import pandas as pd
import pytest

from paint.data.kinematic_stac import make_kinematic_item


@pytest.fixture
def kinematic_item_data() -> Tuple[str, pd.Series]:
    """
    Make a fixture with data for generating a kinematic item.

    Returns
    -------
    str
        The heliostat ID.
    pd.Series
        The data for the kinematic stac item.
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


def test_make_kinematic_item(kinematic_item_data: Tuple[str, pd.Series]) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    kinematic_item_data : Tuple[str, pd.Series]
        The test fixture.
    """
    heliostat_key, data = kinematic_item_data
    assert isinstance(heliostat_key, str)
    _, item = make_kinematic_item(heliostat_key=heliostat_key, heliostat_data=data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "AA23-kinematic_properties",
        "type": "Feature",
        "title": "Kinematic properties of AA23",
        "description": "The kinematic properties that describe the kinematic applied in AA23",
        "collection": "AA23-heliostat_properties-collection",
        "geometry": {
            "type": "Point",
            "coordinates": [50.913521077320304, 6.38670151979386, 88.711],
        },
        "bbox": [
            50.913501077320305,
            6.38668151979386,
            86.711,
            50.9135410773203,
            6.38672151979386,
            90.711,
        ],
        "properties": {
            "datetime": "2021-07-20Z05:09:29Z",
            "created": "2021-07-20Z05:09:29Z",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-kinematic_properties-stac.json",
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
            "kinematic_properties": {
                "href": "https://paint-database.org/WRI1030197/AA23/Properties/AA23-kinematic_properties.json",
                "roles": ["data"],
                "type": "application/geo+json",
                "title": "Kinematic properties of AA23",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)
