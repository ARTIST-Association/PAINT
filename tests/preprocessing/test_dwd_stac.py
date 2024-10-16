import deepdiff
import pandas as pd
import pytest

from paint.preprocessing.dwd_stac_item import make_dwd_item


@pytest.fixture
def dwd_item_data() -> pd.Series:
    """
    Make a fixture with preprocessing for generating a DWD weather STAC item.

    Returns
    -------
    pd.Series
        The preprocessing for the DWD stac item.
    """
    data = {
        "StationID": 15000,
        "latitude": 50.7983,
        "longitude": 6.0244,
        "Elevation": 231.0,
        "StationName": "Aachen-Orsbach",
        "start": "2021-03-31Z22:00:00Z",
        "end": "2024-02-29Z23:00:00Z",
    }
    return pd.Series(data)


def test_make_dwd_item(dwd_item_data: pd.Series) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    dwd_item_data : pd.Series
        The test fixture.
    """
    item = make_dwd_item(data=dwd_item_data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "dwd-weather",
        "type": "Feature",
        "title": "Weather preprocessing from the DWD",
        "description": "Weather preprocessing from the DWD station ID 15000, i.e. Aachen-Orsbach",
        "collection": "weather-collection",
        "geometry": {"type": "Point", "coordinates": [50.7983, 6.0244, 231.0]},
        "bbox": [50.7983, 6.0244, 231.0, 50.7983, 6.0244, 231.0],
        "properties": {
            "datetime": None,
            "start_datetime": "2021-03-31Z22:00:00Z",
            "end_datetime": "2024-02-29Z23:00:00Z",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/Weather/dwd-weather-item-stac.json",
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
                "href": "https://paint-database.org/WRI1030197/Weather/dwd-weather.h5",
                "roles": ["preprocessing"],
                "type": "application/x-hdf5",
                "title": "Weather preprocessing from the DWD",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)
