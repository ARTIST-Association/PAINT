import deepdiff
import pandas as pd
import pytest

from paint.data.juelich_weather_stac_item import make_juelich_weather_item


@pytest.fixture
def juelich_item_data() -> pd.Series:
    """
    Make a fixture with data for generating a Juelich weather STAC item.

    Returns
    -------
    pd.Series
        The data for the Juelich stac item.
    """
    data = {
        "start": "2020-12-01Z01:32:00Z",
        "end": "2021-01-15Z22:59:59Z",
    }
    return pd.Series(data)


def test_make_juelich_item(juelich_item_data: pd.Series) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    juelich_item_data : pd.Series
        The test fixture.
    """
    item = make_juelich_weather_item(juelich_item_data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "juelich-weather",
        "type": "Feature",
        "title": "Weather data from Juelich",
        "description": "Weather data from the Juelich weather station",
        "collection": "weather-collection",
        "geometry": {"type": "Point", "coordinates": [50.916518, 6.387409, 89]},
        "bbox": [50.916518, 6.387409, 89, 50.916518, 6.387409, 89],
        "properties": {"datetime": "null"},
        "start_datetime": "2020-12-01Z01:32:00Z",
        "end_datetime": "2021-01-15Z22:59:59Z",
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/Weather/juelich-weather-item-stac",
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
                "href": "https://paint-database.org/WRI1030197/Weather/juelich-weather.h5",
                "roles": ["data"],
                "type": "application/x-hdf5",
                "title": "Weather data from the Juelich weather station",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)
