from typing import Tuple

import deepdiff
import pandas as pd
import pytest

from paint.preprocessing.juelich_weather_stac_item import make_juelich_weather_item


@pytest.fixture
def juelich_data() -> Tuple[str, pd.Series]:
    """
    Make a fixture with data for generating a Juelich weather STAC item.

    Returns
    -------
    str
        Month group considered.
    pd.Series
        Data for the Juelich STAC item.
    """
    data = {
        "start": "2020-12-01Z01:32:00Z",
        "end": "2020-12-15Z22:59:59Z",
    }
    return "2020-12", pd.Series(data)


def test_make_juelich_item(juelich_data: tuple[str, pd.Series]) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    data : tuple[str, pd.Series]
        Test fixture.
    """
    month_group, juelich_item_data = juelich_data
    item = make_juelich_weather_item(month_group=month_group, data=juelich_item_data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "2020-12-juelich_weather",
        "type": "Feature",
        "title": "Weather data from Juelich for 2020-12",
        "description": "Weather data from the Juelich weather station for 2020-12",
        "collection": "weather-collection",
        "geometry": {"type": "Point", "coordinates": [50.916518, 6.387409, 89]},
        "bbox": [50.916518, 6.387409, 89, 50.916518, 6.387409, 89],
        "properties": {
            "datetime": None,
            "start_datetime": "2020-12-01Z01:32:00Z",
            "end_datetime": "2020-12-15Z22:59:59Z",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/Weather/2020-12-juelich_weather-item-stac.json",
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
                "href": "https://paint-database.org/WRI1030197/Weather/weather-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": "https://paint-database.org/WRI1030197/Weather/weather-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "weather_data": {
                "href": "https://paint-database.org/WRI1030197/Weather/2020-12-juelich_weather.h5",
                "roles": ["data"],
                "type": "application/x-hdf5",
                "title": "Weather data from the Juelich weather station for 2020-12",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)
